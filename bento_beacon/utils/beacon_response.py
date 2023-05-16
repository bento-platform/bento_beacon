from flask import current_app, g
from .katsu_utils import search_summary_statistics, overview_statistics


def get_censorship_threshold():
    # throws expection if threshold missing from config
    return current_app.config["BEACON_CONFIG"]["smallCellCountThreshold"]


def zero_count_response():
    return beacon_response({"count": 0, "results": []})


def init_response_data():
    # init so always available at endpoints
    g.response_data = {}
    g.response_info = {}


def add_info_to_response(info):
    g.response_info["message"] = info


def add_stats_to_response(ids):
    if ids is not None and len(ids) <= get_censorship_threshold():
        return

    if ids is None:
        stats = overview_statistics()
    else:
        stats = search_summary_statistics(ids)
    packaged_stats = package_biosample_and_experiment_stats(stats)
    g.response_info["bento"] = packaged_stats


def add_overview_stats_to_response():
    add_stats_to_response(None)


def package_biosample_and_experiment_stats(stats):
    biosamples = stats.get("biosamples", {})
    experiments = stats.get("experiments", {})
    biosamples_count = biosamples.get("count", 0)
    experiments_count = experiments.get("count", 0)
    sampled_tissue = biosamples.get("sampled_tissue", {})
    experiment_type = experiments.get("experiment_type", {})

    # TODO: apply censorship here

    # convert to bento_public response format
    sampled_tissue_data = [{"label": key, "value": value} for key, value in sampled_tissue.items()]
    experiment_type_data = [{"label": key, "value": value} for key, value in experiment_type.items()]

    return {
        "biosamples": {"count": biosamples_count, "sampled_tissue": sampled_tissue_data},
        "experiments": {"count": experiments_count, "experiment_type": experiment_type_data}
    }


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
        r["info"] = info

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
    if not collection_response:
        count = results.get("count")
        count = 0 if count <= get_censorship_threshold() else count

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
