import aiohttp
from flask import current_app, request
from functools import reduce
from json import JSONDecodeError
from urllib.parse import urlencode, urlsplit, urlunsplit

from .exceptions import APIException, InvalidQuery
from .http import tcp_connector
from typing import Literal
from .exceptions import APIException, InvalidQuery
from ..authz.access import create_access_header_or_fall_back
from ..authz.headers import auth_header_from_request

RequiresAuthOptions = Literal["none", "forwarded", "full"]


async def katsu_filters_query(beacon_filters, datatype, get_biosample_ids=False, project_id=None, dataset_id=None):
    payload = katsu_json_payload(beacon_filters, datatype, get_biosample_ids)
    response = await katsu_post(payload, project_id=project_id, dataset_id=dataset_id)
    results = response.get("results")
    match_list = []

    if results is None:
        raise APIException(message="error calling metadata service")

    # response correct but nothing found
    if not results:
        return []
        # return {"count": 0, "results": []}

    # possibly multiple projects/datasets, combine results:
    # - count response only wants one count
    # - full record response is split by dataset, but this is reconstructed from ids
    # consider splitting results here once gohan is scoped
    for value in results.values():
        if value.get("data_type") == datatype:
            match_list = match_list + value.get("matches")

    return list(set(match_list))


async def katsu_filters_and_sample_ids_query(beacon_filters, datatype, sample_ids, project_id=None, dataset_id=None):

    # empty query
    if not beacon_filters and not sample_ids:
        return []

    # okay if sample_ids is empty, just don't add "in" statement if missing
    filters_copy = beacon_filters[:]
    if sample_ids:
        filters_copy.append({"id": "biosamples.[item].id", "operator": "#in", "value": sample_ids})
    return await katsu_filters_query(filters_copy, datatype, project_id=project_id, dataset_id=dataset_id)


async def katsu_post(payload, endpoint=None, project_id=None, dataset_id=None):
    c = current_app.config

    # awkward default since current_app not available in function params
    endpoint = c["KATSU_SEARCH_ENDPOINT"] if endpoint is None else endpoint

    query_dict = {}
    if project_id is not None:
        query_dict["project"] = project_id
    if dataset_id is not None:
        query_dict["dataset"] = dataset_id

    url = c["KATSU_BASE_URL"] + endpoint + ("?" + urlencode(query_dict) if query_dict else "")

    current_app.logger.debug(f"calling katsu url {url}")

    try:
        async with aiohttp.ClientSession(connector=tcp_connector(c)) as s:
            async with s.post(
                url, headers=await create_access_header_or_fall_back(), timeout=c["KATSU_TIMEOUT"], json=payload
            ) as r:

                katsu_response = await r.json()

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.error(f"katsu error: JSON decode error with POST {url}")
        raise APIException(message="invalid non-JSON response from katsu")
    except aiohttp.ClientError as e:
        current_app.logger.error(f"katsu error: {e}")
        raise APIException(message="error calling katsu metadata service")

    if not r.ok:
        current_app.logger.error(f"katsu error, status: {r.status}, message: {katsu_response.get('message')}")
        raise APIException(message="error calling katsu metadata service")

    return katsu_response


async def katsu_get(
    endpoint,
    entity_id=None,
    project_id=None,
    dataset_id=None,
    query_dict=None,
    requires_auth: RequiresAuthOptions = "none",
):
    c = current_app.config
    katsu_base_url = c["KATSU_BASE_URL"]
    timeout = c["KATSU_TIMEOUT"]

    query_dict = {} if query_dict is None else query_dict

    if project_id is not None:
        query_dict["project"] = project_id
    if dataset_id is not None:
        query_dict["dataset"] = dataset_id

    # construct request url
    url_components = urlsplit(katsu_base_url)
    id_param = "/" + entity_id if entity_id is not None else ""
    query_url = urlunsplit(
        (
            url_components.scheme,
            url_components.netloc,
            url_components.path + endpoint + id_param,
            urlencode(query_dict),
            url_components.fragment,
        )
    )

    headers = {}
    if requires_auth == "forwarded":
        headers = auth_header_from_request()
    elif requires_auth == "full":
        headers = await create_access_header_or_fall_back()
    try:
        async with aiohttp.ClientSession(connector=tcp_connector(c)) as s:
            async with s.get(query_url, headers=headers, timeout=timeout) as r:
                katsu_response = await r.json()

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.error(f"katsu error: JSON decode error with GET {query_url}")
        raise APIException(message="invalid non-JSON response from katsu")
    except aiohttp.ClientError as e:
        current_app.logger.error(f"katsu error: {e}")
        raise APIException(message="error calling katsu metadata service")

    if not r.ok:
        current_app.logger.error(f"katsu error, status: {r.status}, message: {katsu_response.get('message')}")
        raise APIException(message="error calling katsu metadata service")

    return katsu_response


# -------------------------------------------------------
#       search using katsu public config
# -------------------------------------------------------


async def search_from_config(config_filters, project_id=None, dataset_id=None):
    # query error checking handled in katsu
    query_dict = {cf["id"]: cf["value"] for cf in config_filters}
    response = await katsu_get(
        current_app.config["KATSU_BEACON_SEARCH"],
        project_id=project_id,
        dataset_id=dataset_id,
        query_dict=query_dict,
        requires_auth="full",
    )
    return response.get("matches", [])


async def get_katsu_config_search_fields(project_id=None, dataset_id=None):
    fields = await katsu_get(
        current_app.config["KATSU_PUBLIC_CONFIG_ENDPOINT"],
        project_id=project_id,
        dataset_id=dataset_id,
        requires_auth="forwarded",
    )
    current_app.config["KATSU_CONFIG_SEARCH_FIELDS"] = fields
    return fields


# -------------------------------------------------------
#       query conversion
# -------------------------------------------------------


katsu_operator_mapping = {"=": "#eq", "<": "#lt", "<=": "#le", ">": "#gt", ">=": "#ge"}


# convert an individual beacon filter into bento format
def bento_query_expression(q):
    # break up phenopackets property name with "#resolve" appended at the front
    katsu_key = ["#resolve", *q["id"].split(".")]

    beacon_value = q["value"]
    has_wildcard = "%" in beacon_value

    # reject meaningless cases
    if has_wildcard and q["operator"] in ("<", "<=", ">", ">="):
        raise InvalidQuery("cannot interpret wildcard character '%' with an inequality operator (<, <=, >, >=)")

    # separate handling for negation
    if q["operator"] == "!":
        op = "#ilike" if has_wildcard else "#eq"
        return ["#not", [op, katsu_key, beacon_value]]

    # separate handling for in/list (never negated)
    if q["operator"] == "#in":
        return ["#in", katsu_key, ["#list", *beacon_value]]

    # all other cases
    katsu_op = "#ilike" if has_wildcard else katsu_operator_mapping[q["operator"]]
    return [katsu_op, katsu_key, beacon_value]


# convert an array of beacon filters into an array of bento query terms
def expression_array(terms):
    return list(map(bento_query_expression, terms))


# produce a bento query expression tree from a list of beacon filters
def bento_expression_tree(terms):
    return {} if not terms else reduce(lambda x, y: ["#and", x, y], expression_array(terms))


def katsu_json_payload(filters, datatype, get_biosample_ids):

    id_type = "subject"

    if get_biosample_ids:
        if datatype == "phenopacket":
            id_type = "biosamples"  # plural
        if datatype == "experiment":
            id_type = "biosample"

    return {
        "data_type": datatype,
        "query": bento_expression_tree(filters),
        "output": "values_list",
        "field": [id_type, "id"],
    }


# -------------------------------------------------------
#       filtering terms
# -------------------------------------------------------


async def katsu_config_filtering_terms(project_id, dataset_id):
    filtering_terms = []
    sections = (await get_katsu_config_search_fields(project_id=project_id, dataset_id=dataset_id)).get("sections", [])
    for section in sections:
        for field in section["fields"]:
            filtering_term = {
                "type": "alphanumeric",
                "id": field["id"],
                "label": field["title"],
                #
                # longer lablel / helptext
                "description": field.get("description", ""),
                #
                # bento internal use fields, more to come
                "bento": {"section": section["section_title"]},
                #
                # as of beacon 2.1.1
                "values": field["options"],
                #
                # unimplemented proposal: https://github.com/ga4gh-beacon/beacon-v2/issues/115
                # proposal is for path in beacon spec, so our mapping does not match exactly
                # "target": f["mapping"]
                #
                # possible todo: "scopes" field
                # beacon spec field, not to be confused with bento scope
                # filter scope for us is always all queryable entities in this beacon, but that can vary per beacon
                # we can infer this from the queryable endpoints / blueprints that are active
            }
            filtering_terms.append(filtering_term)

    return filtering_terms


async def get_filtering_terms(project_id, dataset_id):
    # add ontology filters here when we start supporting ontologies
    # could also add filters for phenopacket and experiment queries if user has correct permissions
    return await katsu_config_filtering_terms(project_id, dataset_id)


# -------------------------------------------------------
#       utils
# -------------------------------------------------------


# used by info endpoints that don't check censorship settings
# throws exception for bad scope
async def verify_request_project_scope():
    view_args = request.view_args if request.view_args else {}
    project_id = view_args.get("project_id")
    project_ids = [p["identifier"] for p in (await katsu_projects()).get("results", [])]
    if project_id is not None and project_id not in project_ids:
        raise InvalidQuery(f"No project found with id {project_id}")


async def katsu_total_individuals_count(project_id=None, dataset_id=None):
    c = current_app.config
    endpoint = c["KATSU_INDIVIDUALS_ENDPOINT"]
    count_response = await katsu_get(
        endpoint, query_dict={"page_size": "1"}, requires_auth="full", project_id=project_id, dataset_id=dataset_id
    )
    count = count_response.get("count")
    return count


async def katsu_projects(project_id=None):
    return await katsu_get(
        current_app.config["KATSU_PROJECTS_ENDPOINT"],
        entity_id=project_id,
        query_dict={"format": "phenopackets"},
        requires_auth="none",
    )


async def katsu_datasets(project_id=None):
    # katsu /datasets endpoint not scoped, so call /projects and read from there
    datasets = []
    response = await katsu_projects(project_id=project_id)

    if project_id is not None:  # single project
        datasets.extend(response.get("datasets", []))
    else:  # multiple projects
        projects = response.get("results", [])
        for p in projects:
            datasets.extend(p.get("datasets"))

    return datasets


async def katsu_dataset_by_id(id, project_id=None):
    datasets = await katsu_datasets(project_id=project_id)
    result = [d for d in datasets if d.get("identifier") == id]
    if result:
        return result[0]
    return {}  # or return None?


async def phenopackets_for_ids(ids):
    # retrieve from katsu search
    payload = {"data_type": "phenopacket", "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]]}
    endpoint = current_app.config["KATSU_SEARCH_ENDPOINT"]
    return await katsu_post(payload, endpoint)


async def biosample_ids_for_individuals(individual_ids):
    if not individual_ids:
        return []
    filters = [{"id": "subject.id", "operator": "#in", "value": individual_ids}]
    return await katsu_filters_query(filters, "phenopacket", get_biosample_ids=True)


# scope done elsewhere, summary based on ids
async def search_summary_statistics(ids):
    endpoint = current_app.config["KATSU_SEARCH_OVERVIEW"]
    payload = {"id": ids}
    return await katsu_post(payload, endpoint)


async def overview_statistics(project_id=None, dataset_id=None):
    # call katsu for censored public overview
    stats = await katsu_get(
        current_app.config["KATSU_BEACON_SEARCH"],
        project_id=project_id,
        dataset_id=dataset_id,
        requires_auth="forwarded",
    )

    # here we mostly pass katsu response unmodified
    # extra handling is for edge case where total count is below threshold, when katsu doesn't return any data at all
    individuals_count = stats.get("count", 0)
    biosamples_data = stats.get("biosamples", {})
    experiments_data = stats.get("experiments", {})

    return {
        "biosamples": {
            "count": biosamples_data.get("count", 0),
            "sampled_tissue": biosamples_data.get("sampled_tissue", []),
        },
        "experiments": {
            "count": experiments_data.get("count", 0),
            "experiment_type": experiments_data.get("experiment_type", []),
        },
        "individuals": {"count": individuals_count},
    }


async def katsu_censorship_settings(project_id=None, dataset_id=None) -> tuple[int | None, int | None]:
    rules = await katsu_get(
        current_app.config["KATSU_PUBLIC_RULES"],
        project_id=project_id,
        dataset_id=dataset_id,
        requires_auth="forwarded",
    )
    max_filters = rules.get("max_query_parameters")
    count_threshold = rules.get("count_threshold")
    # return even if None
    return max_filters, count_threshold
