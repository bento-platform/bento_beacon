from unittest.mock import patch
from .data.service_responses import (
    katsu_datasets_response,
    katsu_total_individuals_count_response,
    gohan_counts_for_overview_response,
    katsu_config_search_fields_response,
)
from .conftest import client, validate_response


RESPONSE_SPEC_FILENAMES = {
    "info": "beaconInfoResponse.json",
    "service-info": "ga4gh-service-info-1-0-0-schema.json",
    "map": "beaconMapResponse.json",
    "configuration": "beaconConfigurationResponse.json",
    "entry_types": "beaconEntryTypesResponse.json",
    "filtering_terms": "beaconFilteringTermsResponse.json",
    "count_response": "beaconCountResponse.json",
    "collections_response": "beaconCollectionsResponse.json",
    "results_set_response": "beaconResultsetsResponse.json",
    "error": "beaconErrorResponse.json",
}


# info endpoints
# --------------------------------------------------------


@patch("bento_beacon.endpoints.info.katsu_datasets")
def test_service_info(mock_fn, client):
    mock_fn.return_value = katsu_datasets_response
    response = client.get("/service-info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["service-info"])


@patch("bento_beacon.endpoints.info.katsu_datasets")
def test_root(mock_fn, client):
    mock_fn.return_value = katsu_datasets_response
    response = client.get("/")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


@patch("bento_beacon.endpoints.info.katsu_total_individuals_count")
@patch("bento_beacon.endpoints.info.gohan_counts_for_overview")
@patch("bento_beacon.endpoints.info.katsu_datasets")
def test_info(katsu_datasets_mock, gohan_counts_mock, katsu_total_individuals_mock, client):
    katsu_datasets_mock.return_value = katsu_datasets_response
    gohan_counts_mock.return_value = gohan_counts_for_overview_response
    katsu_total_individuals_mock.return_value = katsu_total_individuals_count_response
    response = client.get("/info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


def test_map(client):
    response = client.get("/map")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["map"])


def test_entry_types(client):
    response = client.get("/entry_types")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["entry_types"])


@patch("bento_beacon.endpoints.info.katsu_datasets")
def test_configuration_endpoint(mock_fn, client):
    mock_fn.return_value = katsu_datasets_response
    response = client.get("/configuration")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["configuration"])


@patch("bento_beacon.utils.katsu_utils.get_katsu_config_search_fields")
def test_filtering_terms(mock_fn, client):
    mock_fn.return_value = katsu_config_search_fields_response
    response = client.get("/filtering_terms")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["filtering_terms"])


@patch("bento_beacon.endpoints.info.katsu_total_individuals_count")
@patch("bento_beacon.endpoints.info.gohan_counts_for_overview")
@patch("bento_beacon.endpoints.info.katsu_datasets")
def test_overview(katsu_datasets_mock, gohan_counts_mock, katsu_total_individuals_mock, client):
    katsu_datasets_mock.return_value = katsu_datasets_response
    gohan_counts_mock.return_value = gohan_counts_for_overview_response
    katsu_total_individuals_mock.return_value = katsu_total_individuals_count_response
    response = client.get("/overview")

    # /overview is bento-only, does not exist in beacon spec
    # currently matches the /info response but with an extra "overview" field in the response.
    assert response.status_code == 200
    assert "overview" in response.get_json().get("response")


# --------------------------------
