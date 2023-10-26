from flask import current_app, g, request
from .katsu_utils import search_summary_statistics, overview_statistics
from .censorship import get_censorship_threshold, censored_count
from .exceptions import InvalidQuery
from ..constants import GRANULARITY_BOOLEAN, GRANULARITY_COUNT, GRANULARITY_RECORD


def zero_count_response():
    return build_query_response(ids=[])


def init_response_data():
    # init so always available at endpoints
    g.response_data = {}
    g.response_info = {}


# TODO: handle multiple messages
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

    # convert to bento_public response format
    sampled_tissue_data = [{"label": key, "value": value} for key, value in sampled_tissue.items()]
    experiment_type_data = [{"label": key, "value": value} for key, value in experiment_type.items()]

    return {
        "biosamples": {"count": biosamples_count, "sampled_tissue": sampled_tissue_data},
        "experiments": {"count": experiments_count, "experiment_type": experiment_type_data}
    }


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


def beacon_full_response(result_sets):
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
    received_request_summary = received_request()
    return {
        "beaconId": current_app.config["BEACON_ID"],
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request_summary
    }


def build_info_response_meta():
    return {
        "beaconId": current_app.config["BEACON_ID"],
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "returnedSchemas": []
    }


def build_response_summary(results, collection_response):
    if not collection_response:
        count = results.get("count")
        count = 0 if count <= get_censorship_threshold() else count

    # single collection (cohort or dataset), possibly empty
    # now incorrect, especially if results are paginated
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

# new configurable response, with granularity and better control flow
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx


def response_granularity():
    """
    Determine response granularity from requested granularity and permissions.
    Returns requested granularity when requested <= max, returns max otherwise,
    where max is the highest granularity allowed, based on this user's permissions
    and the ordering is "boolean" < "count" < "record"
    """
    default_g = current_app.config["DEFAULT_GRANULARITY"].get(request.blueprint)
    max_g = GRANULARITY_RECORD if g.permission_query_data else default_g
    requested_g = g.request_data.get("requestedGranularity")

    # below would be cleaner with an ordered enum, but that adds serialization headaches

    # if max is "record" everything is permitted
    if max_g == GRANULARITY_RECORD:
        return requested_g
    # if max if "boolean" nothing else is permitted
    if max_g == GRANULARITY_BOOLEAN:
        return max_g
    # only thing lower than count is boolean
    if max_g == GRANULARITY_COUNT:
        return requested_g if requested_g == GRANULARITY_BOOLEAN else max_g


def build_query_response(ids=None, numTotalResults=None, full_record_handler=None):
    granularity = response_granularity()
    count = len(ids) if numTotalResults is None else numTotalResults
    returned_count = censored_count(count)
    if granularity == GRANULARITY_BOOLEAN:
        return beacon_boolean_response(returned_count)
    if granularity == GRANULARITY_COUNT:
        return beacon_count_response(returned_count)
    if granularity == GRANULARITY_RECORD:
        if full_record_handler is None:
            # user asked for full response where it doesn't exist yet, eg in variants
            raise InvalidQuery("full response not available for this entry type")
        result_sets, numTotalResults = full_record_handler(ids)
        return beacon_result_set_response(result_sets, numTotalResults)

    # no other cases, throw exception?
    # could add warning to response if not returning requested granularity


def response_meta(returned_schemas, returned_granularity):
    return {
        "beaconId": current_app.config["BEACON_ID"],
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request()
    }


def response_info():
    return getattr(g, "response_info", None)


def schemas_this_request():
    # currently only one possible schema per entry type
    s = current_app.config["ENTRY_TYPES_DETAILS"].get(request.blueprint, {}).get("defaultSchema", {}).get("id")
    return [s]


# censored (or not) according to permissions
def beacon_boolean_response(count):
    returned_schemas = []
    returned_granularity = "boolean"
    r = {
        "meta": response_meta(returned_schemas, returned_granularity),
        "responseSummary": {"exists": count > 0},
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


# censored (or not) according to permissions
def beacon_count_response(count):
    returned_schemas = []
    returned_granularity = "count"
    r = {
        "meta": response_meta(returned_schemas, returned_granularity),
        "responseSummary": {"numTotalResults": count, "exists": count > 0},
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


# response from /cohorts and /datasets
# general info only, currently uncensored, could add filtering by permissions if necessary
def beacon_collections_response(results):
    returned_schemas = schemas_this_request()
    returned_granularity = "record"
    r = {
        "meta": response_meta(returned_schemas, returned_granularity),
        "response": results,
        "response summary": {"exists": "true" if results else False}
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


# uncensored full record response, typically for authorized users
# any fine-grained permissions are handled before we get here
# TODO: pagination (ideally after katsu search gets paginated)
def beacon_result_set_response(result_sets, numTotalResults):
    returned_schemas = schemas_this_request()
    returned_granularity = "record"
    r = {
        "meta": response_meta(returned_schemas, returned_granularity),
        "responseSummary": {"numTotalResults": numTotalResults, "exists": numTotalResults > 0},
        "response": {"resultSets": result_sets}
    }
    info = response_info()
    if info:
        r["info"] = info
    return r
