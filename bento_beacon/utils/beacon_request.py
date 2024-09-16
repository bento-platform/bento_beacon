import jsonschema
from bento_lib.auth.permissions import P_QUERY_DATA
from flask import current_app, request, g
from .exceptions import InvalidQuery
from .censorship import reject_if_too_many_filters
from ..authz.middleware import check_permission


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

    return {"meta": meta, "query": query}


def save_request_data():
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

    request_data = {
        "apiVersion": request_meta.get("apiVersion", defaults["apiVersion"]),
        "requestedSchemas": request_meta.get("requestedSchemas", defaults["requestedSchemas"]),
        "pagination": {**defaults["pagination"], **request_query.get("pagination", {})},
        "requestedGranularity": request_query.get("requestedGranularity", defaults["granularity"]),
    }
    if query_request_parameters:
        request_data["requestParameters"] = query_request_parameters

    if query_filters:
        reject_if_too_many_filters(query_filters)
        request_data["filters"] = query_filters

    if request_bento:
        request_data["bento"] = request_bento

    # raw request data, this is echoed in response "meta" field
    g.request_data = request_data

    # parsed query components
    g.beacon_query_parameters = parse_query_params(request_data)


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


def verify_permissions():
    # can do much more here in the future
    g.permission_query_data = check_permission(P_QUERY_DATA)
