from functools import wraps
from flask import g
from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_DATA,
    P_DOWNLOAD_DATA,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
)
from ..utils.exceptions import PermissionsException

PermissionsDict = dict[Permission, bool]


# perhaps clean up weird mix of approaches for determining scope:

# "dataset_id" param (scope is dataset if it exists, otherwise not)
# "dataset_level" param (bool equivalent of above)
# named scope levels "everything", "project", "dataset"
# ...  plus the resource produced by bento_lib build_resource()


# two possibilities for methods below:
# 1. purely functional (always use permissions parameter)
# 2. no parameter, just pull current permissions from flask g
# ... note that most callers will be pulling permissions from g anyhow,
# alternative is passing request everywhere, but request is also global in flask, so again, there's not much point

# third possibility: decorators


def has_bool_permissions(dataset_id: str, permissions: PermissionsDict) -> bool:
    dataset_level = False if dataset_id is None else True
    bool_permission = bool_permission_for_scope(dataset_level)
    return permissions.get(bool_permission, False)


def has_count_permissions(dataset_id: str, permissions: PermissionsDict) -> bool:
    dataset_level = False if dataset_id is None else True
    count_permission = counts_permission_for_scope(dataset_level)
    return permissions.get(count_permission, False)


# naming is confusing here
# this grants permission to get full record response
# but it also means "all access".... no count threshold, no max filters, no forbidden queries
# are these always going to be the same thing?
# full record response has more in common with P_DOWNLOAD_DATA
def has_full_record_permissions(permissions: PermissionsDict) -> bool:
    return permissions.get(P_QUERY_DATA, False)


def has_download_data_permissions(permissions: PermissionsDict) -> bool:
    return permissions.get(P_DOWNLOAD_DATA, False)


# useful fns stolen from katsu
def bool_permission_for_scope(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def counts_permission_for_scope(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


# why not decorators?
def requires_full_record_permissions(f):
    wraps(f)

    def decorated_func(*args, **kwargs):
        if g.permissions.get(P_QUERY_DATA, False):
            return f(*args, **kwargs)
        else:
            raise PermissionsException()

    return decorated_func
