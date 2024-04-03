from flask import current_app, g
from .exceptions import APIException, InvalidQuery
from .katsu_utils import katsu_censorship_settings


MESSAGE_FOR_CENSORED_QUERY_WITH_NO_RESULTS = "No results. Either none were found, or the query produced results numbering at or below the threshold for censorship."


def set_censorship_settings(max_filters, count_threshold):
    current_app.config["MAX_FILTERS"] = max_filters
    current_app.config["COUNT_THRESHOLD"] = count_threshold


# saves settings to config as a side effect
def censorship_retry() -> tuple[int | None, int | None]:
    max_filters, count_threshold = katsu_censorship_settings()
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


def threshold_retry() -> int | None:
    _, count_threshold = censorship_retry()
    return count_threshold


def max_filters_retry() -> int | None:
    max_filters, _ = censorship_retry()
    return max_filters


def get_censorship_threshold():
    if g.permission_query_data:
        return 0
    threshold = current_app.config["COUNT_THRESHOLD"]
    return threshold if threshold is not None else threshold_retry()


def censored_count(count):
    t = get_censorship_threshold()
    if count <= t:
        return 0
    return count


# we don't have the same option of returning zero here
def get_max_filters():
    max_filters = current_app.config["MAX_FILTERS"]
    return max_filters if max_filters is not None else max_filters_retry()


# ugly side-effect code, but keeps censorship code together
def reject_if_too_many_filters(filters):
    if g.permission_query_data:
        return
    max_filters = get_max_filters()
    if len(filters) > max_filters:
        raise InvalidQuery(f"too many filters in request, maximum of {max_filters} permitted")
