from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from .config_files.config import Config

__all__ = [
    "authz_middleware",
    "PERMISSION_QUERY_PROJECT_LEVEL_BOOLEAN",
    "PERMISSION_QUERY_DATASET_LEVEL_BOOLEAN",
    "PERMISSION_QUERY_PROJECT_LEVEL_COUNTS",
    "PERMISSION_QUERY_DATASET_LEVEL_COUNTS",
    "PERMISSION_QUERY_DATA",
    "PERMISSION_DOWNLOAD_DATA",
]

authz_middleware = FlaskAuthMiddleware(Config.AUTHZ_URL, enabled=Config.AUTHZ_ENABLED)

PERMISSION_QUERY_PROJECT_LEVEL_BOOLEAN = "query:project_level_boolean"
PERMISSION_QUERY_DATASET_LEVEL_BOOLEAN = "query:dataset_level_boolean"
PERMISSION_QUERY_PROJECT_LEVEL_COUNTS = "query:project_level_counts"
PERMISSION_QUERY_DATASET_LEVEL_COUNTS = "query:dataset_level_counts"
PERMISSION_QUERY_DATA = "query:data"
PERMISSION_DOWNLOAD_DATA = "download:data"
