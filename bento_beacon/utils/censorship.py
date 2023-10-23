from flask import current_app, g
from .exceptions import APIException, InvalidQuery


def get_censorship_threshold():
    if g.permission_query_data:
        return 0
    threshold = current_app.config["COUNT_THRESHOLD"]
    if threshold is None:
        raise APIException(message="unable to retrieve 'count_threshold' censorship parameter from katsu")
    return threshold


def censored_count(count):
    t = get_censorship_threshold()
    if count < t:
        return 0
    return count


# we don't have the same option of returning zero here
def get_max_filters():
    max_filters = current_app.config["MAX_FILTERS"]
    if max_filters is None:
        raise APIException(message="unable to retrieve 'max_query_parameters' censorship setting from katsu")
    return max_filters


# ugly side-effect code, but keeps censorship code together
def reject_if_too_many_filters(filters):
    if g.permission_query_data:
        return
    max_filters = get_max_filters()
    if len(filters) > max_filters:
        raise InvalidQuery(f"too many filters in request, maximum of {max_filters} permitted")
