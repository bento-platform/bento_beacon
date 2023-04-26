from flask import current_app, g


def init_response_data():
    # init so always available at endpoints
    g.response_data = {}


def add_info_to_response(info):
    g.response_info = info


def katsu_not_found(r):
    if "count" in r:
        return r["count"] == 0

    # some endpoints return either an object with an id or an error (with no id)
    return "id" not in r


def beacon_response(results, collection_response=False):
    g.request_data["requestedGranularity"] = "record" if collection_response else "count"
    r = {
        "meta": build_response_meta(),
        "responseSummary": build_response_summary(results, collection_response)
    }

    if collection_response:
        r["response"] = results

    info = getattr(g, "response_info", None)
    if info:
        r["info"] = {"message": info}

    return r


def beacon_response_with_handover(result_sets):
    g.request_data["requestedGranularity"] = "record"
    r = {
        "meta": build_response_meta(),
        "responseSummary": {"exists": True},
        "response": {"resultSets": result_sets}
    }

    info = getattr(g, "response_info", None)
    if info:
        r["info"] = info

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
    returned_schemas = g.get("response_data", {}).get("returnedSchemas", [])
    returned_granularity = g.get("response_data", {}).get("returnedGranularity", "count")
    service_info = current_app.config["BEACON_CONFIG"].get("serviceInfo")
    received_request_summary = received_request()
    return {
        "beaconId": service_info.get("id"),
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],   
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request_summary
    }


def build_info_response_meta():
    service_info = current_app.config["BEACON_CONFIG"].get("serviceInfo")
    return {
        "beaconId": service_info.get("id"),
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "returnedSchemas": []
    }


def build_response_details(results):
    return {"resultSets": results}


def build_response_summary(results, collection_response):
    small_cell_count_threshold = current_app.config["SMALL_CELL_COUNT_THRESHOLD"]

    if not collection_response:
        count = results.get("count")
        count = 0 if count <= small_cell_count_threshold else count

    # single collection (cohort or dataset), possibly empty
    elif isinstance(results, dict):
        count = 1 if results else 0

    # else array of collections
    else:
        count = len(results)

    exists = count > 0 if count else False

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
