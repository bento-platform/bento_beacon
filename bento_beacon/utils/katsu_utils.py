from flask import current_app
from json import JSONDecodeError
import requests
from urllib.parse import urljoin, urlsplit, urlunsplit
from .exceptions import APIException
from functools import reduce


def katsu_filters_query(beacon_filters):
    payload = katsu_json_payload(beacon_filters)
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
# TODO: deprecate
def query_katsu(endpoint, id=None, query=None):
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
        url_components.query + "format=phenopackets",
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
def katsu_json_payload(filters):
    return {
        "data_type": "phenopacket",
        "query": bento_expression_tree(filters),
        "output": "values_list",
        "field": ["subject", "id"]
    }


# -------------------------------------------------------
#       filtering terms
# -------------------------------------------------------


def get_filtering_terms():
    # TODO
    return []


def get_filtering_term_resources():
    # TODO
    return []