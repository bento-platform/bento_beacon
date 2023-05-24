from flask import current_app
from json import JSONDecodeError
import requests
from urllib.parse import urlsplit, urlunsplit
from .exceptions import APIException
from functools import reduce


def katsu_filters_query(beacon_filters, datatype, get_biosample_ids=False):
    payload = katsu_json_payload(beacon_filters, datatype, get_biosample_ids)
    response = katsu_network_call(payload)
    results = response.get("results")
    match_list = []

    if results is None:
        raise APIException("error calling metadata service")

    # response correct but nothing found
    if not results:
        return []
        # return {"count": 0, "results": []}

    # possibly multiple tables tables, combine results
    for value in results.values():
        if value.get("data_type") == datatype:
            match_list = match_list + value.get("matches")

    return match_list


def katsu_filters_and_sample_ids_query(beacon_filters, datatype, sample_ids):

    # empty query
    if not beacon_filters and not sample_ids:
        return []

    # okay if sample_ids is empty, just don't add "in" statement if missing
    filters_copy = beacon_filters[:]
    if sample_ids:
        filters_copy.append(
            {"id": "biosamples.[item].id", "operator": "#in", "value": sample_ids}
        )
    return katsu_filters_query(filters_copy, datatype)


def katsu_network_call(payload, endpoint=None):
    c = current_app.config

    # awkward default since current_app not available in function params
    endpoint = c["KATSU_SEARCH_ENDPOINT"] if endpoint is None else endpoint
    url = c["KATSU_BASE_URL"] + endpoint
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
            current_app.logger.warning(
                f"katsu error, status: {r.status_code}, message: {katsu_response.get('message')}")
            raise APIException(
                message=f"error searching katsu metadata service: {katsu_response.get('message')}")

    except JSONDecodeError:
        # katsu returns html for unhandled exceptions, not json
        current_app.logger.debug("katsu error")
        raise APIException()
    except requests.exceptions.RequestException as e:
        current_app.logger.debug(f"katsu error: {e}")
        raise APIException(message="error calling katsu metadata service")

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
#       search using katsu public config
# -------------------------------------------------------


def search_from_config(config_filters):
    # query error checking handled in katsu
    query_string = "&".join(f'{cf["id"]}{cf["operator"]}{cf["value"]}' for cf in config_filters)
    response = katsu_get(current_app.config["KATSU_BEACON_SEARCH"], query=query_string)
    return response.get("matches", [])


def get_katsu_config_search_fields():
    fields = katsu_get(current_app.config["KATSU_PUBLIC_CONFIG_ENDPOINT"])
    current_app.config["KATSU_CONFIG_SEARCH_FIELDS"] = fields
    return fields

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
    return {key: value for (key, value) in r.items() if key != "created" and key != "updated"}


# construct filtering terms collection from katsu autocomplete endpoints
# note: katsu autocomplete endpoints are paginated
# TODO: these could be memoized, either at startup or the first time they're requested
def get_filtering_terms():
    c = current_app.config
    pheno_features = katsu_autocomplete_terms(
        c["KATSU_PHENOTYPIC_FEATURE_TERMS_ENDPOINT"])
    disease_terms = katsu_autocomplete_terms(
        c["KATSU_DISEASES_TERMS_ENDPOINT"])
    sampled_tissue_terms = katsu_autocomplete_terms(
        c["KATSU_SAMPLED_TISSUES_TERMS_ENDPOINT"])
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


def phenopackets_for_ids(ids):
    # retrieve from katsu search
    payload = {
        "data_type": "phenopacket",
        "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]]
    }
    endpoint = current_app.config["KATSU_SEARCH_ENDPOINT"]
    return katsu_network_call(payload, endpoint)


def search_summary_statistics(ids):
    endpoint = current_app.config["KATSU_SEARCH_OVERVIEW"]
    payload = {"id": ids}
    return katsu_network_call(payload, endpoint)


def overview_statistics():
    return katsu_get(current_app.config["KATSU_PRIVATE_OVERVIEW"]).get("data_type_specific", {})
