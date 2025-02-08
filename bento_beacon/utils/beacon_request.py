import jsonschema
from flask import current_app, request, g
from .exceptions import InvalidQuery, PermissionsException
from .scope import MESSAGE_FOR_TOO_MANY_DATASETS
from ..authz.middleware import evaluate_permissions_on_resource, resource_level
from ..authz.utils import PermissionsDict, has_bool_permissions, has_count_permissions, has_full_record_permissions
from ..constants import GRANULARITY_BOOLEAN, GRANULARITY_COUNT, GRANULARITY_RECORD


def request_defaults():
    return {
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "granularity": current_app.config["DEFAULT_GRANULARITY"].get(request.blueprint, None),
        "includeResultsetResponses": "HIT",
        "pagination": {"skip": 0, "limit": current_app.config["DEFAULT_PAGINATION_PAGE_SIZE"]},
        "requestedSchemas": [],
    }


# replace compact phenopacket and experiment ids with native bento format
def expand_path(id):
    return id.replace("/", ".[item].")


def parse_query_params(request_data):
    variants_query = request_data.get("requestParameters", {}).get("g_variant") or {}
    filters = request_data.get("filters") or []
    phenopacket_filters = list(filter(lambda f: f["id"].startswith("phenopacket."), filters))
    experiment_filters = list(filter(lambda f: f["id"].startswith("experiment."), filters))
    config_filters = [f for f in filters if f not in phenopacket_filters and f not in experiment_filters]

    # plural here for future-proofing and best match with other beacons
    # even though we only accept one dataset currently
    dataset_ids = request_data.get("datasets", {}).get("datasetIds", [])
    if len(dataset_ids) > 1:
        raise InvalidQuery(MESSAGE_FOR_TOO_MANY_DATASETS)
    dataset_id = dataset_ids[0] if len(dataset_ids) else None

    view_args = request.view_args if request.view_args else {}
    project_id = view_args.get("project_id")

    if dataset_id and project_id is None:
        raise InvalidQuery("dataset ids require a corresponding project id")

    # strip filter prefixes and convert remaining ids to bento format
    phenopacket_filters = list(
        map(
            lambda f: {
                "id": expand_path(f["id"])[len("phenopacket.") :],
                "operator": f["operator"],
                "value": f["value"],
            },
            phenopacket_filters,
        )
    )
    experiment_filters = list(
        map(
            lambda f: {
                "id": expand_path(f["id"])[len("experiment.") :],
                "operator": f["operator"],
                "value": f["value"],
            },
            experiment_filters,
        )
    )
    return {
        "variants_query": variants_query,
        "phenopacket_filters": phenopacket_filters,
        "experiment_filters": experiment_filters,
        "config_filters": config_filters,
        "dataset_id": dataset_id,
    }


# structure GET params so they match the nested structure in POST
def package_get_params(params):
    param_keys = list(params)

    query_params_primitives = ("includeResultsetResponses", "requestedGranularity", "testMode")
    variant_params_primitives = (
        "alternateBases",
        "aminoacidChange",
        "assemblyId",
        "geneId",
        "genomicAlleleShortForm",
        "mateName",
        "referenceBases",
        "referenceName",
        "variantMaxLength",
        "variantMinLength",
        "variantType",
    )
    variant_params_arrays = ("start", "end")
    pagination_params = ("skip", "limit")

    meta = {}
    if ["apiVersion"] in param_keys:
        meta["apiVersion"] = params["apiVersion"]

    pagination = {}
    for key in pagination_params:
        if key in param_keys:
            pagination[key] = params[key]

    g_variant = {}
    for key in variant_params_primitives:
        if key in param_keys:
            g_variant[key] = params[key]
    for key in variant_params_arrays:
        if key in param_keys:
            g_variant[key] = params.getlist(key)

    query = {"requestParameters": {"g_variant": g_variant}, "pagination": pagination}
    for key in query_params_primitives:
        if key in param_keys:
            query[key] = params[key]
    if "filters" in param_keys:
        query["filters"] = params.getlist("filters")
    if "datasetIds" in param_keys:
        query["datasets"] = {"datasetIds": params.getlist("datasetIds")}

    return {"meta": meta, "query": query}


async def save_request_data():
    defaults = request_defaults()

    if request.method == "POST":
        request_args = request.get_json() or {}
    else:
        request_args = package_get_params(request.args)

    request_meta = request_args.get("meta", {})
    request_query = request_args.get("query", {})
    request_bento = request_args.get("bento", {})
    query_request_parameters = request_query.get("requestParameters")
    query_filters = request_query.get("filters")
    query_dataset_ids = request_query.get("datasets", {}).get("datasetIds")

    request_data = {
        "apiVersion": request_meta.get("apiVersion", defaults["apiVersion"]),
        "requestedSchemas": request_meta.get("requestedSchemas", defaults["requestedSchemas"]),
        "pagination": {**defaults["pagination"], **request_query.get("pagination", {})},
        "requestedGranularity": request_query.get("requestedGranularity", defaults["granularity"]),
    }
    if query_request_parameters:
        request_data["requestParameters"] = query_request_parameters

    if query_filters:
        request_data["filters"] = query_filters

    if query_dataset_ids:
        request_data["datasets"] = {"datasetIds": query_dataset_ids}

    if request_bento:
        request_data["bento"] = request_bento

    # raw request data, this is echoed in response "meta" field
    g.request_data = request_data

    # parsed query components
    g.beacon_query = parse_query_params(request_data)


def validate_request():
    if request.method == "POST":
        request_args = request.get_json() or {}
    else:
        # GET params are not bound by the beaconRequestBody schema
        return

    # file path resolver for local json schema
    resolver = jsonschema.validators.RefResolver(
        base_uri=current_app.config["BEACON_REQUEST_SPEC_URI"],
        referrer=True,
    )

    try:
        jsonschema.validate(
            instance=request_args,
            schema={"$ref": "beaconRequestBody.json"},
            resolver=resolver,
        )

    except jsonschema.exceptions.ValidationError as e:
        raise InvalidQuery(message=f"Bad Request: {e.message}")

    return


def summary_stats_requested():
    return g.request_data.get("bento", {}).get("showSummaryStatistics")


async def verify_permissions():
    view_args = request.view_args if request.view_args else {}
    project_id = view_args.get("project_id")
    dataset_id = g.beacon_query.get("dataset_id")
    permissions = await retrieve_permissions(project_id, dataset_id)
    check_permissions_sufficient_for_request(permissions, dataset_id)


def check_permissions_sufficient_for_request(permissions: PermissionsDict, dataset_id: str):
    # permissions are for the resource being requested
    # we don't need to re-verify which resource is being requested, so we don't need project_id
    # but we do need to know whether we are at dataset level or project level
    # so need either dataset_id or an equivalent is_dataset_level bool
    # TODO
    requested_granularity = g.request_data["requestedGranularity"]

    if requested_granularity == GRANULARITY_RECORD:
        if not has_full_record_permissions(permissions):
            raise PermissionsException()

    if requested_granularity == GRANULARITY_COUNT:
        if not has_count_permissions(dataset_id, permissions):
            raise PermissionsException()

    if requested_granularity == GRANULARITY_BOOLEAN:
        if not has_bool_permissions(dataset_id, permissions):
            raise PermissionsException()


async def retrieve_permissions(project_id: str, dataset_id: str) -> PermissionsDict:
    # for now we only need to check a single resource (either a dataset, a project, or the "everything" resource)
    permissions = await evaluate_permissions_on_resource(project_id, dataset_id)

    # store and return?
    g.permissions = permissions
    return permissions
