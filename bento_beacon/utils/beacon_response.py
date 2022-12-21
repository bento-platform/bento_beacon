from flask import current_app, g, request
from ..service_info import SERVICE_INFO


def katsu_not_found(r):
    if "count" in r:
        return r["count"] == 0

    # some endpoints return either an object with an id or an error (with no id)
    return "id" not in r


def beacon_response(results, info_message=None, collection_response=False):
    granularity = current_app.config["BEACON_GRANULARITY"]
    r = {
        "meta": build_response_meta(),
        "responseSummary": build_response_summary(results, granularity, collection_response)
    }

    if collection_response:
        r["response"] = results

    if info_message:
        r["info"] = info_message

    return r


def beacon_info_response(info, build_meta=True):
    r = {"response": info}
    if build_meta:
        r["meta"] = build_info_response_meta()
    return r


def received_request():
    try:
        r = {**g.request_data}
    except AttributeError:
        # don't rethrow, you'll just loop back here again
        r = {}
    finally:
        return r


def build_response_meta():
    returned_schemas = []
    returned_granularity = current_app.config["BEACON_GRANULARITY"]
    received_request_summary = {}
    if request.method == "POST":
        received_request_summary = received_request()
    return {
        "beaconId": SERVICE_INFO["id"],
        "apiVersion": SERVICE_INFO["version"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request_summary
    }


def build_info_response_meta():
    return {
        "beaconId": SERVICE_INFO["id"],
        "apiVersion": SERVICE_INFO["version"],
        "returned_schemas": []
    }


def build_response_details(results):
    return {"resultSets": results}


def build_response_summary(results, granularity, collection_response):

    print()
    print(f"RESULTS: {results}")
    print()

    if not collection_response:
        count = results.get("count")

    # single collection (cohort or dataset), possibly empty
    elif isinstance(results, dict):
        count = 1 if results else 0

    # else array of collections
    else:
        count = len(results)

    exists = count > 0 if count else False

    if granularity == "boolean":
        return {"exists": exists}

    return {
        "exists": exists,
        "count": count,
    }


def beacon_error_response(message, status_code):
    return {
        "meta": build_response_meta(),
        "error": {
            "errorCode": status_code,
            "errorMessage": message
        }
    }
