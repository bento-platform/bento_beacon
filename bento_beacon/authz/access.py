import functools
import requests
from flask import current_app

from .headers import auth_header_from_request

__all__ = [
    "get_access_token",
    "create_access_header_or_fall_back",
]


@functools.cache
def get_token_endpoint_from_openid_config_url(url: str, validate_ssl: bool = True):
    r = requests.get(url, verify=validate_ssl)
    if not r.ok:
        raise Exception(f"Received not-OK response from OIDC config URL: {r.status_code}")
    return r.json()["token_endpoint"]


def get_access_token() -> str | None:
    logger = current_app.logger

    oidc_config_url = current_app.config["BENTO_OPENID_CONFIG_URL"]
    client_id = current_app.config["CLIENT_ID"]
    client_secret = current_app.config["CLIENT_SECRET"]
    validate_ssl = not current_app.config["BENTO_DEBUG"]

    if not all((oidc_config_url, client_id, client_secret)):
        logger.error(
            "Could not retrieve access token; one of BENTO_OPENID_CONFIG_URL | CLIENT_ID | CLIENT_SECRET is not set"
        )
        return None

    try:
        token_endpoint = get_token_endpoint_from_openid_config_url(oidc_config_url, validate_ssl=validate_ssl)
    except Exception as e:
        logger.error(f"Could not retrieve access token; got exception from OpenID config URL: {e}")
        return None

    token_res = requests.post(
        token_endpoint,
        verify=validate_ssl,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    return token_res.json()["access_token"]


def create_access_header_or_fall_back():
    logger = current_app.logger

    if not current_app.config["AUTHZ_BENTO_REQUESTS_ENABLED"]:
        logger.warning("AUTHZ_BENTO_REQUESTS_ENABLED is false; falling back to request headers")
        return auth_header_from_request()

    access_token = get_access_token()
    if access_token is None:
        logger.error("Could not retrieve access token; falling back to request headers")
        return auth_header_from_request()
    else:
        return {"Authorization": f"Bearer {access_token}"}
