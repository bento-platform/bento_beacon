from flask import request

__all__ = [
    "HTTP_AUTHZ_HEADER",
    "auth_header_from_request",
]

HTTP_AUTHZ_HEADER = "Authorization"


def auth_header_from_request() -> dict[str, str]:
    auth_header = request.headers.get(HTTP_AUTHZ_HEADER)
    return {HTTP_AUTHZ_HEADER: auth_header}
