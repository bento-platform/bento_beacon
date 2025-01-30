from flask import current_app, g, request, url_for
from .katsu_utils import search_summary_statistics, overview_statistics
from .censorship import (
    get_censorship_threshold,
    censored_count,
    censored_chart_data,
    MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS,
)
from ..authz.utils import has_count_permissions, has_full_record_permissions
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
    add_info_to_response(f"censorship threshold: {g.count_threshold}")


async def add_stats_to_response(ids, project_id=None, dataset_id=None):
    stats = await summary_stats(ids, project_id=project_id, dataset_id=dataset_id)
    if stats:
        g.response_info["bento"] = stats


async def add_overview_stats_to_response(project_id=None, dataset_id=None):
    # TODO: check permissions
    # should fail if you don't at least have count rights

    await add_stats_to_response(None, project_id, dataset_id)


async def summary_stats(ids, project_id=None, dataset_id=None):
    # several cases where summary stats are not given:

    # 1. results are below threshold, so all summary stats will be below it as well
    if ids is not None and len(ids) <= (await get_censorship_threshold()):
        return None

    # 2. user does not have count permissions at this scope
    if not has_count_permissions(dataset_id, g.permissions):
        return None

    # 3. count stats don't make sense for a boolean request, regardless of permissions
    if g.request_data.get("requestedGranularity") == GRANULARITY_BOOLEAN:
        return None

    if ids is None:
        return await overview_statistics(project_id=project_id, dataset_id=dataset_id)

    stats = await search_summary_statistics(ids)
    return await package_biosample_and_experiment_stats(stats)


async def package_biosample_and_experiment_stats(stats):
    phenopacket_dts_stats = stats.get("phenopacket", {}).get("data_type_specific", {})
    experiment_stats = stats.get("experiment", {}).get("data_type_specific", {}).get("experiments", {})

    biosamples = phenopacket_dts_stats.get("biosamples", {})
    biosamples_count = biosamples.get("count", 0)
    sampled_tissue = biosamples.get("sampled_tissue", {})

    experiments_count = experiment_stats.get("count", 0)
    experiment_type = experiment_stats.get("experiment_type", {})

    # convert to bento_public response format
    sampled_tissue_data = [{"label": key, "value": value} for key, value in sampled_tissue.items()]
    experiment_type_data = [{"label": key, "value": value} for key, value in experiment_type.items()]

    return {
        "biosamples": {
            "count": await censored_count(biosamples_count),
            "sampled_tissue": await censored_chart_data(sampled_tissue_data),
        },
        "experiments": {
            "count": await censored_count(experiments_count),
            "experiment_type": await censored_chart_data(experiment_type_data),
        },
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


# reconsider this function
# with fine-grained permissions, queries are either permitted or not
# may no longer be feasible to, eg, give a boolean response to a full-record query
# since the query may be blocked at some stage for insufficient permissions
# ... It's perfectly sensible to reject queries for insufficient permissions
def response_granularity():
    """
    Determine response granularity from requested granularity and permissions.
    Returns requested granularity when requested <= max, returns max otherwise,
    where max is the highest granularity allowed, based on this user's permissions
    and the ordering is "boolean" < "count" < "record"
    """

    # GET requests impossible to handle without a default, since "requestedGranularity" exists only in POST body
    default_g = current_app.config["DEFAULT_GRANULARITY"].get(request.blueprint)

    max_g = GRANULARITY_RECORD if has_full_record_permissions(g.permissions) else default_g
    requested_g = g.request_data.get("requestedGranularity")

    # below would be cleaner with an ordered enum, but that adds serialization headaches

    # if max is "record" everything is permitted
    if max_g == GRANULARITY_RECORD:
        return requested_g
    # if max is "boolean" nothing else is permitted
    if max_g == GRANULARITY_BOOLEAN:
        return max_g
    # only thing lower than count is boolean
    if max_g == GRANULARITY_COUNT:
        return requested_g if requested_g == GRANULARITY_BOOLEAN else max_g

    # no other cases
    raise APIException()


async def build_query_response(ids=None, numTotalResults=None, full_record_handler=None):
    granularity = response_granularity()
    count = len(ids) if numTotalResults is None else numTotalResults
    returned_count = await censored_count(count)
    if returned_count == 0 and (await get_censorship_threshold()) > 0:
        add_no_results_censorship_message_to_response()
    if granularity == GRANULARITY_BOOLEAN:
        return beacon_boolean_response(returned_count)
    if granularity == GRANULARITY_COUNT:
        return beacon_count_response(returned_count)
    if granularity == GRANULARITY_RECORD:
        if full_record_handler is None:
            # user asked for full response where it doesn't exist yet, e.g. in variants
            raise InvalidQuery("record response not available for this entry type")
        result_sets, numTotalResults = await full_record_handler(ids)
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
        "receivedRequestSummary": received_request(),
    }


def middleware_meta_callback():
    # meta for error responses from middleware
    # errors don't return schemas or use granularity
    # but strangely both fields are required
    returned_schemas = []
    returned_granularity = None
    return response_meta(returned_schemas, returned_granularity)


# --------------------------------
#  responses
# --------------------------------


def beacon_info_response(info):
    r = {
        "response": info,
        "meta": {
            "beaconId": current_app.config["BEACON_ID"],
            "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
            "returnedSchemas": info_endpoint_schema(),
        },
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


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
        "responseSummary": {"exists": True if results else False},
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
        "response": {"resultSets": result_sets},
    }
    info = response_info()
    if info:
        r["info"] = info
    return r


def beacon_error_response(message, status_code):
    return {"meta": response_meta([], None), "error": {"errorCode": status_code, "errorMessage": message}}


async def zero_count_response():
    return await build_query_response(ids=[])


# --------------------------------
#  utils
# --------------------------------


def response_info():
    return getattr(g, "response_info", None)


def info_endpoint_schema():
    path_without_optional_project_id = url_for(request.endpoint)
    return [current_app.config["INFO_ENDPOINTS_SCHEMAS"][path_without_optional_project_id]]


def schemas_this_query():
    endpoint_set = current_app.config["ENTRY_TYPES_DETAILS"][request.blueprint]
    entityType = endpoint_set["entryType"]  # confusion between "entityType" and "entryType" is part of beacon spec
    schema = endpoint_set["defaultSchema"]["id"]
    return [{"entityType": entityType, "schema": schema}]
