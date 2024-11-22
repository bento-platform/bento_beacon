import os
import pathlib
from urllib.parse import urlunsplit
from flask import current_app
import jsonschema
import pytest
import responses
from .data.service_responses import (
    katsu_datasets_response,
    katsu_config_search_fields_response,
    katsu_private_search_response,
    katsu_private_search_overview_response,
    katsu_public_search_response,
    katsu_public_rules_response,
    katsu_individuals_response,
    gohan_search_response,
    token_response,
)

TESTS_DIR = pathlib.Path(__file__).parent.absolute()
BEACON_RESPONSE_SPEC_RELATIVE_PATH = "beacon-v2/framework/json/responses/"
AUTHZ_URL = "http://bento-authz.local"
KATSU_URL = "http://katsu.local"
GOHAN_URL = "http://gohan.local"
OPENID_CONFIG_URL = AUTHZ_URL + "/fake/openid-configuration"
TOKEN_URL = AUTHZ_URL + "/fake/token"

MOCK_ACCESS_TOKEN = "fakeToken"
token_endpoint_config_response = {
    "token_endpoint": TOKEN_URL,
}


@pytest.fixture
def beacon_test_app():
    mock_config_files_dir = TESTS_DIR / "data"
    os.environ.update(
        {
            "CONFIG_ABSOLUTE_PATH": str(mock_config_files_dir),
            "BENTOV2_DOMAIN": "test.local",
            "BENTOV2_PUBLIC_URL": "http://test.local",
            "BEACON_BASE_URL": "http://test.local/api/beacon",
            "BENTO_BEACON_VERSION": "test",
            "KATSU_BASE_URL": KATSU_URL,
            "BEACON_KATSU_TIMEOUT": "1",
            "GOHAN_BASE_URL": GOHAN_URL,
            "BEACON_GOHAN_TIMEOUT": "1",
            "DRS_URL": "http://drs.local",
            "REFERENCE_URL": "http://reference.local",
            "MAX_RETRIES_FOR_CENSORSHIP_PARAMS": "-1",  # "-1" retries = don't try at all
            "BENTO_AUTHZ_SERVICE_URL": AUTHZ_URL,
            "BENTO_OPENID_CONFIG_URL": OPENID_CONFIG_URL,
            "BEACON_CLIENT_ID": "aggregation",
            "BEACON_CLIENT_SECRET": "FAKE123",
            "BENTO_VALIDATE_SSL": "false",
        }
    )

    from bento_beacon.app import app

    yield app


@pytest.fixture
def client(beacon_test_app):
    return beacon_test_app.test_client()


@pytest.fixture
def app_config(beacon_test_app):
    with beacon_test_app.app_context():
        yield current_app.config


def validate_response(response, schema_filename):
    beacon_response_spec_dir = urlunsplit(("file", str(TESTS_DIR.parent), BEACON_RESPONSE_SPEC_RELATIVE_PATH, "", ""))
    jsonschema.validate(
        instance=response,
        schema={"$ref": schema_filename},
        resolver=jsonschema.validators.RefResolver(
            base_uri=beacon_response_spec_dir,
            referrer=True,
        ),
    )


# ------------------------------
# mock external api calls
# could parameterize the different endpoint urls,
# but main danger is the endpoints changing in the services themselves, but that's not tested here


def authz_everything_true(count=1):
    mock_post(f"{AUTHZ_URL}/policy/evaluate", {"result": [[True] for _ in range(count)]})


def authz_everything_false(count=1):
    mock_post(f"{AUTHZ_URL}/policy/evaluate", {"result": [[False] for _ in range(count)]})


def auth_get_oidc_token():
    auth_oidc_token_config()
    auth_oidc_token_response()


def auth_oidc_token_config():
    mock_get(OPENID_CONFIG_URL, token_endpoint_config_response)


def auth_oidc_token_response():
    mock_post(TOKEN_URL, token_response)


def katsu_config_search_fields():
    mock_get(f"{KATSU_URL}/api/public_search_fields", {"result": katsu_config_search_fields_response})


def katsu_private_search():
    mock_post(f"{KATSU_URL}/private/search", katsu_private_search_response)


def katsu_private_search_overview():
    mock_post(f"{KATSU_URL}/api/search_overview", katsu_private_search_overview_response)


def katsu_datasets():
    mock_get(f"{KATSU_URL}/api/datasets", katsu_datasets_response)


def katsu_individuals():
    mock_get(f"{KATSU_URL}/api/individuals", katsu_individuals_response)


def katsu_public_search():
    mock_get(f"{KATSU_URL}/api/public", katsu_public_search_response)


def katsu_public_rules():
    mock_get(f"{KATSU_URL}/api/public_rules", katsu_public_rules_response)


def gohan_search():
    mock_get(f"{GOHAN_URL}/variants/get/by/variantId", gohan_search_response)


def gohan_overview():
    mock_get(f"{GOHAN_URL}/variants/overview", gohan_search_response)


def mock_get(url, response):
    responses.get(url, json=response)


def mock_post(url, response):
    # ignore request payload
    responses.post(url, json=response)


# add github test workflow
