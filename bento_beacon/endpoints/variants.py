import requests
from flask import Blueprint, jsonify, current_app, request

from utils.beacon_request import map_beacon_query_to_gohan_query

variants = Blueprint("variants", __name__)

GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"


@variants.route("/g_variants", methods=['GET', 'POST'])
def get_variants():

    # check if auth level correct for this query
    # validate query
    # map to gohan query

    args = request.values
    print(args)

    gohan_query = map_beacon_query_to_gohan_query()

    granularity = current_app.config["BEACON_GRANULARITY"]

    # if granularity is count or boolean, call gohan count endpoint /variants/count/by/variantId?
    r = query_gohan(
        gohan_query) if granularity == 'record' else query_gohan_count_only(gohan_query)

    # else use /variants/get/by/variantId?

    # if get, package url ags into dict
    # if post, package payload into dict

    # CHANGE TO ZERO-BASED COORDINATES !!

    # call gohan with dict in request payload
    # process gohan repsonse into beacon format
    # return beacon response (or beacon error )

    # example gohan call:
    # https://portal.bentov2.local/api/gohan/variants/get/by/variantId?lowerBound=25911206&upperBound=45911206&size=1000&sortByPosition=desc&assemblyId=GRCh37

    return {"variants": "TODO"}


@variants.route("/g_variants/<id>", methods=['GET', 'POST'])
def variant_by_id(id):
    # get one variant by (internal?) id
    return {"variant by id": "TODO"}


@variants.route("/g_variants/<id>/biosamples", methods=['GET', 'POST'])
def biosamples_by_variant(id):
    # all biosamples for a particular variant
    return {"variant biosamples": "TODO"}


@variants.route("/g_variants/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_variant(id):
    # all individuals for a particular variant
    return {"individual variants": "TODO"}


# gohan queries:
# TODO: ADD ARGS TO QUERY

# GET /variants/get/by/variantId
def query_gohan(query):
    print("query gohan")
    config = current_app.config

    query_url = config["GOHAN_BASE_URL"] + GOHAN_SEARCH_ENDPOINT
    verify_certificates = not config["BENTO_DEBUG"]
    timeout = config["GOHAN_TIMEOUT"]

    params = {
        "lowerBound": 25911206,
        "upperBound": 45911206,
        "size": 1000,
        "sortByPosition": "desc",
        "assemblyId": "GRCh37",
        "chromosome": 17
    }

    print(f"query_url: {query_url}")

    print(f"verify_certificates: {verify_certificates}")
    print(f"timeout: {timeout}")

    r = requests.get(
        query_url,
        verify=verify_certificates,
        timeout=timeout,
        params=params
    )

    print("gohan response")
    print(r._content)

    pass

# GET /variants/count/by/variantId


def query_gohan_count_only(query):
    print("query gohan counts")

    query_url = current_app.config["GOHAN_BASE_URL"] + GOHAN_COUNT_ENDPOINT

    pass
