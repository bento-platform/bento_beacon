from flask import current_app
from ..service_info import SERVICE_INFO


def map_gohan_response_to_beacon_reponse(r):
    pass


def map_katsu_response_to_beacon_response(r):

    # TODO: full mapping
    return {"response": r}


def katsu_not_found(r):
    if "count" in r:
        return r["count"] == 0

    # some endpoints return either an object with an id or an error (with no id)
    return "id" not in r


def beacon_not_found_response_details():
    pass


def beacon_response(results):
    return {
        "meta": build_response_meta(),
        "response": build_response_details(results),
        "responseSummary": build_response_summary(results)
    }


def build_response_meta():
    # -------------------
    # TODO, parameterize all
    returned_schemas = {}
    returned_granularity = current_app.config["BEACON_GRANULARITY"]
    received_request_summary = {}
    # --------------------
    return {
        "beaconId": SERVICE_INFO["id"],
        "apiVersion": SERVICE_INFO["version"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request_summary
    }


def build_response_details(results):
    # TODO: parameterize to count and boolean granularity
    return {"resultSets": results}


def build_response_summary(results):
    count = len(results)
    exists = count > 0

    # only "exists" is required so count can be masked if necessary to avoid re-identification attack
    return {
        "exists": exists,
        "count": count,
    }
