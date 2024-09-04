from flask import request, Request


def auth_header_getter(r: Request) -> dict[str, str]:
    token = r.headers.get("authorization")
    return {"Authorization": token} if token else {}


def auth_header_from_request() -> dict[str, str]:
    return auth_header_getter(request)
