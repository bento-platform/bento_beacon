from typing import Literal
from flask import request
from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_DATA,
    P_DOWNLOAD_DATA,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
)

from ..config_files.config import Config
from ..utils.beacon_response import middleware_meta_callback

__all__ = [
    "authz_middleware",
    "check_permission",
]


authz_middleware = FlaskAuthMiddleware(
    Config.AUTHZ_URL,
    enabled=Config.AUTHZ_ENABLED,
    beacon_meta_callback=middleware_meta_callback,
    debug_mode=Config.BENTO_DEBUG,
)

permissions_by_scope_level = {
    "everything": [
        P_QUERY_DATA,
        P_DOWNLOAD_DATA,
        P_QUERY_PROJECT_LEVEL_COUNTS,
        P_QUERY_PROJECT_LEVEL_BOOLEAN,
        P_QUERY_DATASET_LEVEL_COUNTS,
        P_QUERY_DATASET_LEVEL_BOOLEAN,
    ],
    # same as "everything" :(  xxxxxxxxxxxx
    "project": [
        P_QUERY_DATA,
        P_DOWNLOAD_DATA,
        P_QUERY_PROJECT_LEVEL_COUNTS,
        P_QUERY_PROJECT_LEVEL_BOOLEAN,
        P_QUERY_DATASET_LEVEL_COUNTS,
        P_QUERY_DATASET_LEVEL_BOOLEAN,
    ],
    "dataset": [P_QUERY_DATA, P_DOWNLOAD_DATA, P_QUERY_DATASET_LEVEL_COUNTS, P_QUERY_DATASET_LEVEL_BOOLEAN],
}


async def evaluate_permissions_on_resource(resource: dict) -> dict[Permission, bool]:
    """
    Returns a dict of permissions types and true/false for each one,
    e.g. {P_QUERY_DATA: false, P_QUERY_PROJECT_LEVEL_COUNTS: true, ... }
    """
    # permissions are checked in katsu, so some code here will be redundant in some cases, but:
    # - it's not checked yet in gohan
    # - in many cases beacon needs uncensored katsu data, and has to check permissions itself

    level = resource_level(resource)
    checked_permissions = permissions_by_scope_level[level]
    r = await authz_middleware.async_evaluate_to_dict(request, [resource], checked_permissions, mark_authz_done=True)
    return r[0] if r else {}


def resource_level(resource: dict) -> Literal["everything", "project", "dataset"]:
    level = "everything"
    if resource.get("project"):
        if resource.get("dataset"):
            level = "dataset"
        else:
            level = "project"
    return level
