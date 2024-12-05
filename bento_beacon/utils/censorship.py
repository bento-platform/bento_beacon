from flask import current_app, g, request
from .exceptions import APIException, InvalidQuery
from .katsu_utils import katsu_censorship_settings


MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS = "No results. Either none were found, or the query produced results numbering at or below the threshold for censorship."


async def set_censorship() -> None:
    reject_query_if_not_permitted()
    await get_censorship_settings_for_this_request()
    await reject_if_too_many_filters()


async def censorship_settings_lookup() -> tuple[int, int]:
    # we're "before request" but view args are available from request object
    view_args = request.view_args if request.view_args else {}
    project_id = view_args.get("project_id")
    dataset_id = view_args.get("dataset_id")

    max_filters, count_threshold = await katsu_censorship_settings(project_id=project_id, dataset_id=dataset_id)
    if max_filters is None or count_threshold is None:
        raise APIException(
            message="error reading censorship settings from katsu: "
            + f"project_id: {project_id}, dataset_id: {dataset_id}, max_filters: {max_filters}, count_threshold: {count_threshold}"
        )

    current_app.logger.info(f"censorship for this request: {max_filters}, count_threshold: {count_threshold}")
    return max_filters, count_threshold


async def get_censorship_settings_for_this_request() -> None:
    g.max_filters, g.count_threshold = await censorship_settings_lookup()


async def threshold_retry() -> int:
    _, count_threshold = await censorship_settings_lookup()
    g.count_threshold = count_threshold
    return count_threshold


async def max_filters_retry() -> int:
    max_filters, _ = await censorship_settings_lookup()
    g.max_filters = max_filters
    return max_filters


async def get_censorship_threshold() -> int:
    if g.permission_query_data:
        return 0
    threshold = g.get("count_threshold")
    return threshold if threshold is not None else await threshold_retry()


async def censored_count(count) -> int:
    t = await get_censorship_threshold()
    if count <= t:
        return 0
    return count


# we don't have the same option of returning zero here
async def get_max_filters() -> int:
    max_filters = g.get("max_filters")
    return max_filters if max_filters is not None else await max_filters_retry()


# ugly side-effect code, but keeps censorship code together
async def reject_if_too_many_filters() -> None:
    if g.permission_query_data:
        return
    max_filters = await get_max_filters()
    request_filters = g.get("request_data", {}).get("filters")
    if len(request_filters) > max_filters:
        raise InvalidQuery(f"too many filters in request, maximum of {max_filters} permitted")


# at some point may want to show censored fields as zero rather than removing entirely
async def censored_chart_data(data) -> list[dict[str, int]]:
    t = await get_censorship_threshold()  # zero with correct permissions
    return [{"label": d["label"], "value": d["value"]} for d in data if d["value"] > t]


def query_has_phenopacket_filter() -> bool:
    return bool(g.beacon_query_parameters["phenopacket_filters"])


def query_has_experiment_filter() -> bool:
    return bool(g.beacon_query_parameters["experiment_filters"])


# some anonymous queries are not permitted
def reject_query_if_not_permitted() -> None:
    if g.permission_query_data or not current_app.config["ANONYMOUS_METADATA_QUERY_USES_DISCOVERY_CONFIG_ONLY"]:
        return
    if query_has_phenopacket_filter() or query_has_experiment_filter():
        raise InvalidQuery("anonymous queries should use filters from discovery config only")
