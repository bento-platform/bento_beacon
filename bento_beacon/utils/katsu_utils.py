from flask import current_app
from json import JSONDecodeError
import requests
from urllib.parse import urlsplit, urlunsplit
from .exceptions import APIException, InvalidQuery
from functools import reduce


def katsu_filters_query(beacon_filters, get_biosample_ids=False):

    # reject if too many filters
    max_filters = current_app.config["MAX_FILTERS"]
    if max_filters > 0 and len(beacon_filters) > max_filters:
        raise InvalidQuery(f"too many filters in request, maximum of {max_filters} permitted")

    payload = katsu_json_payload(beacon_filters, get_biosample_ids)
    response = katsu_network_call(payload)
    results = response.get("results")
    match_list = []

    if results is None:
        raise APIException("error calling metadata service")

    # response correct but nothing found
    if not results:
        return {"count": 0, "results": []}

    # possibly multiple phenopackets tables, combine results
    for value in results.values():
        if value.get("data_type") == "phenopacket":
            match_list = match_list + value.get("matches")

    return {"count": len(match_list), "results": match_list}


def katsu_filters_and_sample_ids_query(beacon_filters, sample_ids):
    # hardcoded phenopackets linked field id, TODO: parameterize
    in_statement = {"id": "biosamples.[item].id", "operator": "#in", "value": sample_ids}
    filters_and_in = [*beacon_filters, in_statement]
    return katsu_filters_query(filters_and_in)


def katsu_network_call(payload):
    c = current_app.config
    url = c["KATSU_BASE_URL"] + c["KATSU_SEARCH_ENDPOINT"]
    current_app.logger.debug(f'calling katsu url {url}')

    try:
        r = requests.post(
            url,
            verify=not c["DEBUG"],
            timeout=c["KATSU_TIMEOUT"],
            json=payload
        )

        katsu_response = r.json()
        if not r.ok:
            current_app.logger.warning(f"katsu error, status: {r.status_code}, message: {katsu_response.get('message')}")
            raise APIException(message=f"error searching katsu metadata service: {katsu_response.get('message')}")

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.debug("katsu error")
        raise APIException()

    return katsu_response


# used for GET calls at particular katsu endpoints, eg /biosamples
def katsu_get(endpoint, id=None, query=""):
    c = current_app.config
    katsu_base_url = c["KATSU_BASE_URL"]
    verify_certificates = not c["DEBUG"]
    timeout = current_app.config["KATSU_TIMEOUT"]

    # construct request url 
    url_components = urlsplit(katsu_base_url)
    id_param = "/" + id if id is not None else ""
    query_url = urlunsplit((
        url_components.scheme,
        url_components.netloc,
        url_components.path + endpoint + id_param,
        url_components.query + query,
        url_components.fragment
        ))

    print("before request")

    try:
        r = requests.get(
            query_url,
            verify=verify_certificates,
            timeout=timeout
        )
        katsu_response = r.json()

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.debug("katsu error")
        raise APIException()

    return katsu_response


# -------------------------------------------------------
#       query conversion
# -------------------------------------------------------


katsu_operator_mapping = {
    "=": "#eq",
    "<": "#lt",
    "<=": "#le",
    ">": "#gt",
    ">=": "#ge"
}


# assume json query already validated
# convert an individual beacon filter into bento format
def bento_query_expression(q):
    # break up phenopackets property name with "#resolve" appended at the front
    katsu_key = ["#resolve", *q["id"].split(".")]

    # extra handling for negation, "!" is always negated equality
    if q["operator"] == "!":
        return ["#not", ["#eq", katsu_key, q["value"]]]

    # separate handling for in/list 
    if q["operator"] == "#in":
        return ["#in", katsu_key, ["#list", *q["value"]]]

    return [katsu_operator_mapping[q["operator"]], katsu_key, q["value"]]


# convert an array of beacon filters into an array of bento query terms
def expression_array(terms):
    return list(map(bento_query_expression, terms))


# produce a bento query expression tree from a list of beacon filters
def bento_expression_tree(terms):
    return {} if not terms else reduce(lambda x, y: ["#and", x, y], expression_array(terms))


# TODO: parameterize data_type and field
def katsu_json_payload(filters, get_biosample_ids):
    id_type = "biosamples" if get_biosample_ids else "subject"

    return {
        "data_type": "phenopacket",
        "query": bento_expression_tree(filters),
        "output": "values_list",
        "field": [id_type, "id"]
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
    return {key: value for (key, value) in r.items() if key != "created" and key != "updated" }


# construct filtering terms collection from katsu autocomplete endpoints
# note: katsu autocomplete endpoints are paginated
# TODO: these could be memoized, either at startup or the first time they're requested
def get_filtering_terms():
    c = current_app.config
    pheno_features = katsu_autocomplete_terms(c["KATSU_PHENOTYPIC_FEATURE_TERMS_ENDPOINT"])
    disease_terms = katsu_autocomplete_terms(c["KATSU_DISEASES_TERMS_ENDPOINT"])
    sampled_tissue_terms = katsu_autocomplete_terms(c["KATSU_SAMPLED_TISSUES_TERMS_ENDPOINT"])
    filtering_terms = pheno_features + disease_terms + sampled_tissue_terms
    return list(map(katsu_autocomplete_to_beacon_filter, filtering_terms))


def get_filtering_term_resources():
    r = katsu_get(current_app.config["KATSU_RESOURCES_ENDPOINT"])
    resources = r.get("results", [])
    resources = list(map(katsu_resources_to_beacon_resource, resources))
    return resources

# -------------------------------------------------------
#       utils
# -------------------------------------------------------


def katsu_total_individuals_count():
    c = current_app.config
    endpoint = c["KATSU_INDIVIDUALS_ENDPOINT"]
    count_response = katsu_get(endpoint, query="page_size=1")
    count = count_response.get("count")
    return count


def katsu_datasets(id=None):
    c = current_app.config
    endpoint = c["KATSU_DATASETS_ENDPOINT"]
    response = katsu_get(endpoint, id, query="format=phenopackets")
    if "detail" in response and response["detail"] == "Not found.":
        return {}

    if "results" in response:
        return response.get("results")  # collection

    return response  # single dataset
