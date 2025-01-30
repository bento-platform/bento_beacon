from typing import Literal
from flask import request, current_app
from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_DATA,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
)
from bento_lib.auth.resources import build_resource, RESOURCE_EVERYTHING

# from bento_lib.auth.types import EvaluationResultDict
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
        P_QUERY_PROJECT_LEVEL_COUNTS,
        P_QUERY_PROJECT_LEVEL_BOOLEAN,
        P_QUERY_DATASET_LEVEL_COUNTS,
        P_QUERY_DATASET_LEVEL_BOOLEAN,
    ],
    # same as "everything" :(  xxxxxxxxxxxx
    "project": [
        P_QUERY_DATA,
        P_QUERY_PROJECT_LEVEL_COUNTS,
        P_QUERY_PROJECT_LEVEL_BOOLEAN,
        P_QUERY_DATASET_LEVEL_COUNTS,
        P_QUERY_DATASET_LEVEL_BOOLEAN,
    ],
    "dataset": [P_QUERY_DATA, P_QUERY_DATASET_LEVEL_COUNTS, P_QUERY_DATASET_LEVEL_BOOLEAN],
}


async def check_permission(permission: Permission) -> bool:
    return await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, permission, mark_authz_done=True)


async def evaluate_permissions_on_resource(project_id: str, dataset_id: str) -> dict[Permission, bool]:
    """
    Returns a dict of permissions types and true/false for each one,
    e.g. {P_QUERY_DATA: false, P_QUERY_PROJECT_LEVEL_COUNTS: true, ... }
    """
    # permissions are checked in katsu, so some code here will be redundant in some cases, but:
    # - it's not checked yet in gohan
    # - in some cases (like overviews) beacon needs uncensored katsu data, and has to check permissions itself

    resource = build_resource(project_id, dataset_id)
    level = resource_level(project_id, dataset_id)  # or something else?

    checked_permissions = permissions_by_scope_level[level]
    r = await authz_middleware.async_evaluate_to_dict(request, [resource], checked_permissions, mark_authz_done=True)
    return r[0] if r else {}


# better typing here, perhaps "Level" from lib middleware
def resource_level(project_id=None, dataset_id=None) -> Literal["everything", "project", "dataset"]:
    level = "everything"
    if project_id:
        if dataset_id:
            level = "dataset"
        else:
            level = "project"
    return level
