from flask import request
from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from bento_lib.auth.permissions import Permission
from bento_lib.auth.resources import RESOURCE_EVERYTHING
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
    debug_mode=Config.BENTO_DEBUG
)


def check_permission(permission: Permission) -> bool:
    return authz_middleware.evaluate_one(request, RESOURCE_EVERYTHING, permission, mark_authz_done=True)
