import responses

from .conftest import (
    validate_response,
    authz_everything_true,
    authz_everything_false,
    auth_get_oidc_token,
    katsu_config_response,
    katsu_datasets,
    katsu_private_search,
    katsu_private_overview,
    katsu_private_search_overview,
    katsu_individuals,
    katsu_public_search,
    gohan_search,
    gohan_overview,
)


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


@responses.activate
def test_service_info(client):
    katsu_datasets()
    response = client.get("/service-info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["service-info"])


@responses.activate
def test_root(client):
    katsu_datasets()
    response = client.get("/")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


@responses.activate
def test_info(client):
    katsu_datasets()
    gohan_overview()
    katsu_individuals()
    response = client.get("/info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


def test_map(client):
    response = client.get("/map")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["map"])


def test_entry_types(client):
    response = client.get("/entry_types")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["entry_types"])


@responses.activate
def test_configuration_endpoint(client):
    katsu_datasets()
    response = client.get("/configuration")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["configuration"])


@responses.activate
def test_filtering_terms(client):
    katsu_config_response()
    response = client.get("/filtering_terms")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["filtering_terms"])

@responses.activate
def test_overview(client):
    katsu_datasets()
    gohan_overview()
    katsu_individuals()
    response = client.get("/overview")

    # /overview is bento-only, does not exist in beacon spec
    # currently matches the /info response but with an extra "overview" field in the response.
    assert response.status_code == 200
    assert "overview" in response.get_json().get("response")


# --------------------------------

request_body = {
    "meta": {"apiVersion": "2.0.0"},
    "query": {
        "requestParameters": {
            "g_variant": {"referenceName": "3", "start": [189631388], "assemblyId": "GRCh38", "end": [189897276]}
        },
        "filters": [{"id": "sex", "operator": "=", "value": "FEMALE"}],
    },
    "bento": {"showSummaryStatistics": True},
}


@responses.activate
def test_datasets(client):
    authz_everything_true()
    katsu_config_response()
    katsu_datasets()
    response = client.get("/datasets")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["collections_response"])


@responses.activate
def test_individuals_no_query(client):
    authz_everything_true()
    katsu_individuals()
    response = client.get("/individuals")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["count_response"])


@responses.activate
def test_individuals_query_no_token(client):
    authz_everything_true()
    auth_get_oidc_token()
    katsu_public_search()
    katsu_private_search()
    katsu_private_search_overview()
    gohan_search()
    response = client.post("/individuals", json=request_body)
    data = response.get_json()

    # waiting for fixes to beacon spec before we do any json verification here
    # https://github.com/ga4gh-beacon/beacon-v2/issues/176
    # https://github.com/ga4gh-beacon/beacon-v2/pull/107

    # for now just check that response makes sense
    assert "responseSummary" in data
    assert "numTotalResults" in data["responseSummary"]
