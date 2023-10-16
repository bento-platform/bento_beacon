from flask import request
from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from ..config_files.config import Config
from ..utils.beacon_response import build_response_meta
from .headers import auth_header_getter

authz_middleware = FlaskAuthMiddleware(
    Config.AUTHZ_URL,
    enabled=Config.AUTHZ_ENABLED,
    beacon_meta_callback=build_response_meta,
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
        headers_getter=auth_header_getter,  # currently same as middleware default, so can be removed
    )["result"]
    authz_middleware.mark_authz_done(request)
    return auth_res
