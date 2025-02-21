import jsonschema
import os
import pathlib
from urllib.parse import urlunsplit
from aioresponses import aioresponses
from flask import current_app
import pytest


TESTS_DIR = pathlib.Path(__file__).parent.absolute()
BEACON_RESPONSE_SPEC_RELATIVE_PATH = "beacon-v2/framework/json/responses/"
AUTHZ_URL = "http://bento-authz.local"
KATSU_URL = "http://katsu.local"
GOHAN_URL = "http://gohan.local"
OPENID_CONFIG_URL = AUTHZ_URL + "/fake/openid-configuration"
TOKEN_URL = AUTHZ_URL + "/fake/token"

TOKEN_ENDPOINT_CONFIG_RESPONSE = {
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
            "BEACON_BASE_URL": "https://test.local/api/beacon",
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
            "BENTO_BEACON_NETWORK_ENABLED": "true",
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


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m


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
