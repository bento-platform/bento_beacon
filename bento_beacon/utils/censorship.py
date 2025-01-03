from flask import current_app, g
from .exceptions import APIException, InvalidQuery
from .katsu_utils import katsu_censorship_settings


MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS = "No results. Either none were found, or the query produced results numbering at or below the threshold for censorship."


def set_censorship_settings(max_filters, count_threshold):
    current_app.config["MAX_FILTERS"] = max_filters
    current_app.config["COUNT_THRESHOLD"] = count_threshold


# saves settings to config as a side effect
async def censorship_retry() -> tuple[int | None, int | None]:
    max_filters, count_threshold = await katsu_censorship_settings()
    if max_filters is None or count_threshold is None:
        raise APIException(
            message="error reading censorship settings from katsu: "
            + f"max_filters: {max_filters}, count_threshold: {count_threshold}"
        )

    current_app.logger.info(
        f"setting censorship parameters max_filters: {max_filters}, count_threshold: {count_threshold}"
    )
    set_censorship_settings(max_filters, count_threshold)
    return max_filters, count_threshold


async def threshold_retry() -> int | None:
    _, count_threshold = await censorship_retry()
    return count_threshold


async def max_filters_retry() -> int | None:
    max_filters, _ = await censorship_retry()
    return max_filters


async def get_censorship_threshold():
    if g.permission_query_data:
        return 0
    threshold = current_app.config["COUNT_THRESHOLD"]
    return threshold if threshold is not None else (await threshold_retry())


async def censored_count(count):
    t = await get_censorship_threshold()
    if count <= t:
        return 0
    return count


# we don't have the same option of returning zero here
async def get_max_filters():
    max_filters = current_app.config["MAX_FILTERS"]
    return max_filters if max_filters is not None else await max_filters_retry()


# ugly side-effect code, but keeps censorship code together
async def reject_if_too_many_filters(filters):
    if g.permission_query_data:
        return
    max_filters = await get_max_filters()
    if len(filters) > max_filters:
        raise InvalidQuery(f"too many filters in request, maximum of {max_filters} permitted")


# at some point may want to show censored fields as zero rather than removing entirely
async def censored_chart_data(data):
    t = await get_censorship_threshold()  # zero with correct permissions
    return [{"label": d["label"], "value": d["value"]} for d in data if d["value"] > t]


def query_has_phenopacket_filter():
    return bool(g.beacon_query_parameters["phenopacket_filters"])


def query_has_experiment_filter():
    return bool(g.beacon_query_parameters["experiment_filters"])


# some anonymous queries are not permitted
def reject_query_if_not_permitted():
    if g.permission_query_data or not current_app.config["ANONYMOUS_METADATA_QUERY_USES_DISCOVERY_CONFIG_ONLY"]:
        return
    if query_has_phenopacket_filter() or query_has_experiment_filter():
        raise InvalidQuery("anonymous queries should use filters from discovery config only")
