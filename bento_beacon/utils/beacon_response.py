from flask import current_app, g, request
from .katsu_utils import search_summary_statistics, overview_statistics
from .censorship import get_censorship_threshold, censored_count, MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS
from .exceptions import InvalidQuery, APIException
from ..constants import GRANULARITY_BOOLEAN, GRANULARITY_COUNT, GRANULARITY_RECORD


def init_response_data():
    # init so always available at endpoints
    g.response_data = {}
    g.response_info = {}


def add_info_to_response(info):
    add_message({"description": info, "level": "info"}) 


def add_message(message_obj):
    messages = g.response_info.get("messages", [])
    messages.append(message_obj)
    g.response_info["messages"] = messages


def add_no_results_censorship_message_to_response():
    add_info_to_response(MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS)
    add_info_to_response(f"censorship threshold: {current_app.config['COUNT_THRESHOLD']}")


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


def received_request():
    try:
        r = {**g.request_data}
    except AttributeError:
        # don't rethrow, you'll just loop back here again
        r = {}
    finally:
        return r


# --------------------------------------------------------------------
#  Response control flow
#
#  - determine response granularity (boolean, count, record) from
#    permissions and user request, then route response accordingly
#
#  - apply censorship to bool and count responses for anonymous users;
#    full-record censorship is done elsewhere, typically by not
#    permitting a response
# --------------------------------------------------------------------


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
    
    # no other cases
    raise APIException()


def build_query_response(ids=None, numTotalResults=None, full_record_handler=None):
    granularity = response_granularity()
    count = len(ids) if numTotalResults is None else numTotalResults
    returned_count = censored_count(count)
    if returned_count == 0 and get_censorship_threshold() > 0:
        add_no_results_censorship_message_to_response()
    if granularity == GRANULARITY_BOOLEAN:
        return beacon_boolean_response(returned_count)
    if granularity == GRANULARITY_COUNT:
        return beacon_count_response(returned_count)
    if granularity == GRANULARITY_RECORD:
        if full_record_handler is None:
            # user asked for full response where it doesn't exist yet, e.g. in variants
            raise InvalidQuery("record response not available for this entry type")
        result_sets, numTotalResults = full_record_handler(ids)
        return beacon_result_set_response(result_sets, numTotalResults)


# --------------------------------
#  response meta
# --------------------------------


def response_meta(returned_schemas, returned_granularity):
    return {
        "beaconId": current_app.config["BEACON_ID"],
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request()
    }


def middleware_meta_callback():
    # meta for error responses from middleware
    # errors don't return schemas or use granularity
    # but stragely both fields are required
    returned_schemas = []
    returned_granularity = None
    return response_meta(returned_schemas, returned_granularity)


# --------------------------------
#  responses
# --------------------------------


def beacon_info_response(info):
    return {
        "response": info,
        "meta": {
            "beaconId": current_app.config["BEACON_ID"],
            "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
            "returnedSchemas": info_endpoint_schema()
        }
    }


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
    returned_schemas = schemas_this_query()
    returned_granularity = "record"
    r = {
        "meta": response_meta(returned_schemas, returned_granularity),
        "response": results,
        "responseSummary": {"exists": True if results else False}
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


# uncensored full record response, typically for authorized users
# any fine-grained permissions are handled before we get here
# TODO: pagination (ideally after katsu search gets paginated)
def beacon_result_set_response(result_sets, numTotalResults):
    returned_schemas = schemas_this_query()
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


def beacon_error_response(message, status_code):
    return {
        "meta": response_meta([], None),
        "error": {
            "errorCode": status_code,
            "errorMessage": message
        }
    }


def zero_count_response():
    return build_query_response(ids=[])


# --------------------------------
#  utils
# --------------------------------


def response_info():
    return getattr(g, "response_info", None)


def info_endpoint_schema():
    return [current_app.config["INFO_ENDPOINTS_SCHEMAS"][request.path]]


def schemas_this_query():
    endpoint_set = current_app.config["ENTRY_TYPES_DETAILS"][request.blueprint]
    entityType = endpoint_set["entryType"]  # confusion between "entityType" and "entryType" is part of beacon spec
    schema = endpoint_set["defaultSchema"]["id"]
    return [{"entityType": entityType, "schema": schema}]
