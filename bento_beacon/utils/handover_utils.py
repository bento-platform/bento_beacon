from flask import request, url_for
from urllib.parse import urlsplit, urlunsplit

TRUNCATED_BY_GATEWAY = "api/beacon"


def get_handover_url():
    base_url_components = urlsplit(request.url)
    handover_scheme = "https"
    handover_path = TRUNCATED_BY_GATEWAY + url_for("handover.get_handover")
    handover_base_url = urlunsplit((
        handover_scheme,
        base_url_components.netloc,
        handover_path,
        base_url_components.query,
        base_url_components.fragment
        ))
    return handover_base_url
