from flask import current_app
from json import JSONDecodeError
import requests
from urllib.parse import urlsplit, urlunsplit
from .exceptions import APIException
from functools import reduce

def query_katsu(endpoint, id=None, query=None):
    c = current_app.config
    katsu_base_url = c["KATSU_BASE_URL"]
    verify_certificates = not c["BENTO_DEBUG"]
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

    except JSONDecodeError as e:
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
def bento_query_expression(q):
    # break up phenopackets property name with "#resolve" appended at the front
    katsu_key = ["#resolve", *q["id"].split(".")]

    # extra handling for negation, "!" is always negated equality
    if q["operator"] == "!":
        return ["#not", ["#eq", katsu_key, q["value"]]]

    return [katsu_operator_mapping[q["operator"]], katsu_key, q["value"]]


def expression_array(terms):
    return list(map(bento_query_expression, terms))


def bento_expression_tree(terms):
    return reduce(lambda x, y: ["#and", x, y], expression_array(terms))


def generate_katsu_query(q):
    # input: beacon alphanumeric filtering terms in json/dict format eg: 

    # {
    #     "id": "biosamples.[item].histological_diagnosis.label",        ...or format to be determined
    #     "operator": "=",
    #     "value": "Medulloblastoma"
    # }

    # output: 
    # Bento-style katsu query:
    # ["#ico", ["#resolve", "biosamples", "[item]", "histological_diagnosis", "label"], "Medulloblastoma"]

    # somewhat equivalent js code to build query (form)
    # https://github.com/bento-platform/bento_web/blob/d083e94d956658f56f8ae8ae127966bdbad74ae9/src/utils/search.js#L52-L59

    pass

