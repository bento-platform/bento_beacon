from flask import request
from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from ..config_files.config import Config
from ..utils.beacon_response import middleware_meta_callback

__all__ = [
    "authz_middleware",
    "PERMISSION_QUERY_PROJECT_LEVEL_BOOLEAN",
    "PERMISSION_QUERY_DATASET_LEVEL_BOOLEAN",
    "PERMISSION_QUERY_PROJECT_LEVEL_COUNTS",
    "PERMISSION_QUERY_DATASET_LEVEL_COUNTS",
    "PERMISSION_QUERY_DATA",
    "PERMISSION_DOWNLOAD_DATA",
    "check_permissions",
    "check_permission"
]


authz_middleware = FlaskAuthMiddleware(
    Config.AUTHZ_URL,
    enabled=Config.AUTHZ_ENABLED,
    beacon_meta_callback=middleware_meta_callback,
    debug_mode=Config.BENTO_DEBUG
)

# for now, these will go unused - Beacon currently does not have a strong concept of Bento projects/datasets
PERMISSION_QUERY_PROJECT_LEVEL_BOOLEAN = "query:project_level_boolean"
PERMISSION_QUERY_DATASET_LEVEL_BOOLEAN = "query:dataset_level_boolean"
PERMISSION_QUERY_PROJECT_LEVEL_COUNTS = "query:project_level_counts"
PERMISSION_QUERY_DATASET_LEVEL_COUNTS = "query:dataset_level_counts"
# these permissions can open up various aspects of handoff / full-search
PERMISSION_QUERY_DATA = "query:data"
PERMISSION_DOWNLOAD_DATA = "download:data"


def check_permissions(permissions: list[str]) -> bool:
    auth_res = authz_middleware.authz_post(request, "/policy/evaluate", body={
        "requested_resource": {"everything": True},
        "required_permissions": permissions,
        },
    )["result"]
    authz_middleware.mark_authz_done(request)
    return auth_res


def check_permission(permission: str) -> bool:
    return check_permissions([permission])
