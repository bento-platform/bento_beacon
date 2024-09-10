import aiohttp
from flask import current_app
from functools import reduce
from json import JSONDecodeError
from urllib.parse import urlsplit, urlunsplit

from .exceptions import APIException, InvalidQuery
from .http import tcp_connector
from ..authz.headers import auth_header_from_request


async def katsu_filters_query(beacon_filters, datatype, get_biosample_ids=False):
    payload = katsu_json_payload(beacon_filters, datatype, get_biosample_ids)
    response = await katsu_network_call(payload)
    results = response.get("results")
    match_list = []

    if results is None:
        raise APIException(message="error calling metadata service")

    # response correct but nothing found
    if not results:
        return []
        # return {"count": 0, "results": []}

    # possibly multiple projects/datasets, combine results
    # TODO: revist when we clarify relationship between project and beacons
    for value in results.values():
        if value.get("data_type") == datatype:
            match_list = match_list + value.get("matches")

    return list(set(match_list))


async def katsu_filters_and_sample_ids_query(beacon_filters, datatype, sample_ids):

    # empty query
    if not beacon_filters and not sample_ids:
        return []

    # okay if sample_ids is empty, just don't add "in" statement if missing
    filters_copy = beacon_filters[:]
    if sample_ids:
        filters_copy.append({"id": "biosamples.[item].id", "operator": "#in", "value": sample_ids})
    return await katsu_filters_query(filters_copy, datatype)


async def katsu_network_call(payload, endpoint=None):
    c = current_app.config

    # awkward default since current_app not available in function params
    endpoint = c["KATSU_SEARCH_ENDPOINT"] if endpoint is None else endpoint
    url = c["KATSU_BASE_URL"] + endpoint
    current_app.logger.debug(f"calling katsu url {url}")

    try:
        async with aiohttp.ClientSession(connector=tcp_connector(c)) as s:
            r = await s.post(url, headers=auth_header_from_request(), timeout=c["KATSU_TIMEOUT"], json=payload)
            katsu_response = await r.json()

        if not r.ok:
            current_app.logger.warning(f"katsu error, status: {r.status}, message: {katsu_response.get('message')}")
            raise APIException(message=f"error searching katsu metadata service: {katsu_response.get('message')}")

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.error(f"katsu error: JSON decode error with POST {url}")
        raise APIException(message="invalid non-JSON response from katsu")
    except aiohttp.ClientError as e:
        current_app.logger.error(f"katsu error: {e}")
        raise APIException(message="error calling katsu metadata service")

    return katsu_response


# used for GET calls at particular katsu endpoints, eg /biosamples
async def katsu_get(endpoint, id=None, query=""):
    c = current_app.config
    katsu_base_url = c["KATSU_BASE_URL"]
    timeout = c["KATSU_TIMEOUT"]

    # construct request url
    url_components = urlsplit(katsu_base_url)
    id_param = "/" + id if id is not None else ""
    query_url = urlunsplit(
        (
            url_components.scheme,
            url_components.netloc,
            url_components.path + endpoint + id_param,
            url_components.query + query,
            url_components.fragment,
        )
    )

    try:
        async with aiohttp.ClientSession(tcp_connector(c)) as s:
            r = await s.get(query_url, timeout=timeout)
        katsu_response = await r.json()

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.error(f"katsu error: JSON decode error with GET {query_url}")
        raise APIException(message="invalid non-JSON response from katsu")
    except aiohttp.ClientError as e:
        current_app.logger.error(f"katsu error: {e}")
        raise APIException(message="error calling katsu metadata service")

    return katsu_response


# -------------------------------------------------------
#       search using katsu public config
# -------------------------------------------------------


async def search_from_config(config_filters):
    # query error checking handled in katsu
    query_string = "&".join(f'{cf["id"]}{cf["operator"]}{cf["value"]}' for cf in config_filters)
    response = await katsu_get(current_app.config["KATSU_BEACON_SEARCH"], query=query_string)
    return response.get("matches", [])


async def get_katsu_config_search_fields():
    fields = await katsu_get(current_app.config["KATSU_PUBLIC_CONFIG_ENDPOINT"])
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


def katsu_autocomplete_terms(endpoint):
    return katsu_get(endpoint).get("results", [])


def katsu_autocomplete_to_beacon_filter(a):
    return {"type": "alphanumeric", "id": a.get("id"), "label": a.get("text")}


# strip meaningless timestamps from resouce
def katsu_resources_to_beacon_resource(r):
    return {key: value for (key, value) in r.items() if key != "created" and key != "updated"}


async def katsu_config_filtering_terms():
    filtering_terms = []
    sections = (await get_katsu_config_search_fields()).get("sections", [])
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
                # unimplemented proposal: https://github.com/ga4gh-beacon/beacon-v2/pull/160
                # optionally move to "bento" field if never adopted
                "values": field["options"],
                #
                # another unimplemented proposal: https://github.com/ga4gh-beacon/beacon-v2/issues/115
                # proposal is for path in beacon spec, so our mapping does not match exactly
                # "target": f["mapping"]
                #
                # TODO: scopes
                # filter scope for us is always all queryable entities in this beacon, but that can vary per beacon
                # we can infer this from the queryable endpoints / blueprints that are active
            }
            filtering_terms.append(filtering_term)

    return filtering_terms


#  memoize?
async def get_filtering_terms():
    # add ontology filters here when we start supporting ontologies
    # could also add filters for phenopacket and experiment queries
    return await katsu_config_filtering_terms()


# -------------------------------------------------------
#       utils
# -------------------------------------------------------


async def katsu_total_individuals_count():
    c = current_app.config
    endpoint = c["KATSU_INDIVIDUALS_ENDPOINT"]
    count_response = await katsu_get(endpoint, query="page_size=1")
    count = count_response.get("count")
    return count


async def katsu_datasets(id=None):
    c = current_app.config
    endpoint = c["KATSU_DATASETS_ENDPOINT"]
    try:
        response = await katsu_get(endpoint, id, query="format=phenopackets")
    except APIException:
        return {}

    if "detail" in response and response["detail"] == "Not found.":
        return {}

    if "results" in response:
        return response.get("results")  # collection

    return response  # single dataset


async def phenopackets_for_ids(ids):
    # retrieve from katsu search
    payload = {"data_type": "phenopacket", "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]]}
    endpoint = current_app.config["KATSU_SEARCH_ENDPOINT"]
    return await katsu_network_call(payload, endpoint)


async def biosample_ids_for_individuals(individual_ids):
    if not individual_ids:
        return []
    filters = [{"id": "subject.id", "operator": "#in", "value": individual_ids}]
    return await katsu_filters_query(filters, "phenopacket", get_biosample_ids=True)


async def search_summary_statistics(ids):
    endpoint = current_app.config["KATSU_SEARCH_OVERVIEW"]
    payload = {"id": ids}
    return await katsu_network_call(payload, endpoint)


async def overview_statistics():
    return await katsu_get(current_app.config["KATSU_PRIVATE_OVERVIEW"])


async def katsu_censorship_settings() -> tuple[int | None, int | None]:
    # TODO: should be project-dataset scoped
    rules = await katsu_get(current_app.config["KATSU_PUBLIC_RULES"])
    max_filters = rules.get("max_query_parameters")
    count_threshold = rules.get("count_threshold")
    # return even if None
    return max_filters, count_threshold


def katsu_not_found(r) -> bool:
    if "count" in r:
        return r["count"] == 0

    # some endpoints return either an object with an id or an error (with no id)
    return "id" not in r
