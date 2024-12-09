import aiocache
import aiohttp
from flask import current_app
from .headers import auth_header_from_request
from ..utils.http import tcp_connector

__all__ = [
    "get_access_token",
    "create_access_header_or_fall_back",
]


@aiocache.cached()
async def get_token_endpoint_from_openid_config_url(url: str):
    async with aiohttp.ClientSession(connector=tcp_connector(current_app.config)) as s:
        async with s.get(url) as r:

            if not r.ok:
                raise Exception(f"Received not-OK response from OIDC config URL: {r.status_code}")

            response = await r.json()
    return response["token_endpoint"]


async def get_access_token() -> str | None:
    logger = current_app.logger

    oidc_config_url = current_app.config["OPENID_CONFIG_URL"]
    client_id = current_app.config["CLIENT_ID"]
    client_secret = current_app.config["CLIENT_SECRET"]

    if not all((oidc_config_url, client_id, client_secret)):
        logger.error("Could not retrieve access token; one of OPENID_CONFIG_URL | CLIENT_ID | CLIENT_SECRET is not set")
        return None

    try:
        token_endpoint = await get_token_endpoint_from_openid_config_url(oidc_config_url)
        current_app.logger.info(f"token_endpoint: {token_endpoint}")
    except Exception as e:
        logger.error(f"Could not retrieve access token; got exception from OpenID config URL: {e}")
        return None

    async with aiohttp.ClientSession(connector=tcp_connector(current_app.config)) as s:
        async with s.post(
            token_endpoint,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        ) as token_res:

            res = await token_res.json()

            if not token_res.ok:
                logger.error(f"Could not retrieve access token; got error response: {res}")
                return None

    return res["access_token"]


async def create_access_header_or_fall_back():
    logger = current_app.logger

    if not current_app.config["AUTHZ_BENTO_REQUESTS_ENABLED"]:
        logger.warning("AUTHZ_BENTO_REQUESTS_ENABLED is false; falling back to request headers")
        return auth_header_from_request()

    access_token = await get_access_token()
    if access_token is None:
        logger.error("create_access_header_or_fall_back: falling back to request headers")
        return auth_header_from_request()
    else:
        return {"Authorization": f"Bearer {access_token}"}
