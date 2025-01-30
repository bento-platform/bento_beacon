from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_DATA,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
)

PermissionsDict = dict[Permission, bool]


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
def has_full_record_permissions(permissions: PermissionsDict) -> bool:
    return permissions.get(P_QUERY_DATA, False)


# useful fns stolen from katsu
def bool_permission_for_scope(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def counts_permission_for_scope(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS
