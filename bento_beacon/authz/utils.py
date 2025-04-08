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


def has_bool_permissions(is_dataset_level: bool, permissions: PermissionsDict) -> bool:
    bool_permission = bool_permission_for_scope(is_dataset_level)
    return permissions.get(bool_permission, False)


def has_count_permissions(is_dataset_level: bool, permissions: PermissionsDict) -> bool:
    count_permission = counts_permission_for_scope(is_dataset_level)
    return permissions.get(count_permission, False)


def has_full_record_permissions(permissions: PermissionsDict) -> bool:
    return permissions.get(P_QUERY_DATA, False)


def has_download_data_permissions(permissions: PermissionsDict) -> bool:
    return permissions.get(P_DOWNLOAD_DATA, False)


def bool_permission_for_scope(is_dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if is_dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def counts_permission_for_scope(is_dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if is_dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


def requires_full_record_permissions(f):
    wraps(f)

    async def decorated_func(*args, **kwargs):
        if g.permissions.get(P_QUERY_DATA, False):
            return await f(*args, **kwargs)
        else:
            raise PermissionsException(f"Insufficient permissions: requires permission {P_QUERY_DATA}")

    return decorated_func
