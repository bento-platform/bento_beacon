import copy
from .data.service_responses import (
    katsu_projects_response,
    katsu_public_rules_response,
    katsu_config_search_fields_response,
    gohan_search_response,
    katsu_private_search_response,
    katsu_public_search_response,
    katsu_private_search_overview_response,
    katsu_individuals_response,
    token_response,
)

from .conftest import (
    validate_response,
    TOKEN_ENDPOINT_CONFIG_RESPONSE,
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


# --------------------------------------------------------
# mocks
# --------------------------------------------------------

BEACON_REQUEST_BODY = {
    "meta": {"apiVersion": "2.0.0"},
    "query": {
        "requestParameters": {
            "g_variant": {"referenceName": "3", "start": [189631388], "assemblyId": "GRCh38", "end": [189897276]}
        },
        "filters": [{"id": "sex", "operator": "=", "value": "FEMALE"}],
    },
    "bento": {"showSummaryStatistics": True},
}

SCOPE_EXAMPLE_PROJECT = "fake_project_123"
SCOPE_EXAMPLE_DATASET = "abc123"

SCOPED_BEACON_REQUEST_BODY = copy.deepcopy(BEACON_REQUEST_BODY)
SCOPED_BEACON_REQUEST_BODY["query"]["datasets"] = {"datasetIds": [SCOPE_EXAMPLE_DATASET]}

# aioresponses includes query params when matching urls
KATSU_QUERY_PARAMS = "sex=FEMALE"
KATSU_QUERY_PARAMS_SCOPED = f"sex=FEMALE&project={SCOPE_EXAMPLE_PROJECT}&dataset={SCOPE_EXAMPLE_DATASET}"
GOHAN_QUERY_PARAMS = "assemblyId=GRCh38&chromosome=3&getSampleIdsOnly=True&lowerBound=189631389&upperBound=189897276"


def mock_retrieve_token(app_config, aioresponse):
    openid_config_url = app_config["OPENID_CONFIG_URL"]
    token_url = app_config["AUTHZ_URL"] + "/fake/token"
    aioresponse.get(openid_config_url, payload=TOKEN_ENDPOINT_CONFIG_RESPONSE)
    aioresponse.post(token_url, payload=token_response, repeat=True)


def mock_permissions_all(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[True]]})


def mock_permissions_none(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[False]]})


def mock_katsu_public_rules(app_config, aioresponse):
    public_rules_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PUBLIC_RULES"]
    aioresponse.get(public_rules_url, payload=katsu_public_rules_response)


def mock_katsu_public_rules_scoped(app_config, aioresponse):
    public_rules_url = (
        app_config["KATSU_BASE_URL"] + app_config["KATSU_PUBLIC_RULES"] + "?" + f"project={SCOPE_EXAMPLE_PROJECT}"
    )
    aioresponse.get(public_rules_url, payload=katsu_public_rules_response)


def mock_katsu_projects(app_config, aioresponse):
    projects_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PROJECTS_ENDPOINT"] + "?format=phenopackets"
    aioresponse.get(projects_url, payload=katsu_projects_response)


def mock_katsu_public_search_fields(app_config, aioresponse):
    search_fields_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PUBLIC_CONFIG_ENDPOINT"]
    aioresponse.get(search_fields_url, payload=katsu_config_search_fields_response)


def mock_katsu_public_search_no_query(app_config, aioresponse):
    public_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_BEACON_SEARCH"]
    aioresponse.get(public_search_url, payload=katsu_public_search_response)


def mock_katsu_public_search_query(app_config, aioresponse):
    public_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_BEACON_SEARCH"] + "?" + KATSU_QUERY_PARAMS
    aioresponse.get(public_search_url, payload=katsu_public_search_response)


def mock_katsu_public_search_query_scoped(app_config, aioresponse):
    public_search_url = (
        app_config["KATSU_BASE_URL"] + app_config["KATSU_BEACON_SEARCH"] + "?" + KATSU_QUERY_PARAMS_SCOPED
    )
    aioresponse.get(public_search_url, payload=katsu_public_search_response)


def mock_katsu_private_search_query(app_config, aioresponse):
    private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    aioresponse.post(private_search_url, payload=katsu_private_search_response)


def mock_katsu_private_search_query_scoped(app_config, aioresponse):
    private_search_url = (
        app_config["KATSU_BASE_URL"]
        + app_config["KATSU_SEARCH_ENDPOINT"]
        + "?"
        + f"project={SCOPE_EXAMPLE_PROJECT}&dataset={SCOPE_EXAMPLE_DATASET}"
    )
    aioresponse.post(private_search_url, payload=katsu_private_search_response)


def mock_katsu_private_search_overview(app_config, aioresponse):
    search_overview_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_OVERVIEW"]
    aioresponse.post(search_overview_url, payload=katsu_private_search_overview_response)


def mock_katsu_individuals(app_config, aioresponse):
    individuals_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_INDIVIDUALS_ENDPOINT"] + "?page_size=1"
    aioresponse.get(individuals_url, payload=katsu_individuals_response)


def mock_katsu_individuals_scoped(app_config, aioresponse):
    individuals_url = (
        app_config["KATSU_BASE_URL"]
        + app_config["KATSU_INDIVIDUALS_ENDPOINT"]
        + f"?page_size=1&project={SCOPE_EXAMPLE_PROJECT}"
    )
    aioresponse.get(individuals_url, payload=katsu_individuals_response)


def mock_gohan_overview(app_config, aioresponse):
    gohan_overview_url = app_config["GOHAN_BASE_URL"] + app_config["GOHAN_OVERVIEW_ENDPOINT"]
    aioresponse.get(gohan_overview_url, payload=gohan_search_response)


def mock_gohan_query(app_config, aioresponse):
    gohan_search_url = app_config["GOHAN_BASE_URL"] + app_config["GOHAN_SEARCH_ENDPOINT"] + "?" + GOHAN_QUERY_PARAMS
    aioresponse.get(gohan_search_url, payload=gohan_search_response)


# --------------------------------------------------------
# info endpoints
# --------------------------------------------------------


def test_service_info(client):
    response = client.get("/service-info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["service-info"])


def test_root(client):
    response = client.get("/")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


def test_info(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_katsu_public_search_no_query(app_config, aioresponse)
    mock_katsu_individuals(app_config, aioresponse)
    mock_gohan_overview(app_config, aioresponse)
    response = client.get("/info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])


def test_map(client):
    response = client.get("/map")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["map"])


def test_entry_types(client):
    response = client.get("/entry_types")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["entry_types"])


def test_configuration_endpoint(app_config, client, aioresponse):
    response = client.get("/configuration")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["configuration"])


def test_filtering_terms(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_fields(app_config, aioresponse)
    response = client.get("/filtering_terms")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["filtering_terms"])


def test_overview(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_individuals(app_config, aioresponse)
    mock_katsu_public_search_no_query(app_config, aioresponse)
    mock_gohan_overview(app_config, aioresponse)
    response = client.get("/overview")

    # /overview endpoint is bento-only, does not exist in beacon spec
    # currently matches the /info response but with an extra "overview" field in the response.
    assert response.status_code == 200
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["info"])
    assert "overview" in response.get_json().get("response")


# --------------------------------------------------------
# entities
# --------------------------------------------------------


def test_datasets(app_config, client, aioresponse):
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_permissions_all(app_config, aioresponse)
    response = client.get("/datasets")
    assert response.status_code == 200
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["collections_response"])


def test_individuals_no_query(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_individuals(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    response = client.get("/individuals")
    assert response.status_code == 200
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["count_response"])


def test_individuals_no_query_project_scoped(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_individuals_scoped(app_config, aioresponse)
    mock_katsu_public_rules_scoped(app_config, aioresponse)
    response = client.get(f"/{SCOPE_EXAMPLE_PROJECT}/individuals")
    assert response.status_code == 200
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["count_response"])


# --------------------------------------------------------
# queries
# --------------------------------------------------------


def test_individuals_query_all_permissions(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_REQUEST_BODY)
    data = response.get_json()

    # waiting for fixes to beacon spec before we do any json verification here
    # https://github.com/ga4gh-beacon/beacon-v2/issues/176
    # https://github.com/ga4gh-beacon/beacon-v2/pull/107

    # for now just check that response makes sense
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 4


def test_individuals_query_scoped(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules_scoped(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse)
    mock_katsu_public_search_query_scoped(app_config, aioresponse)
    mock_katsu_private_search_query_scoped(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post(f"/{SCOPE_EXAMPLE_PROJECT}/individuals", json=SCOPED_BEACON_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 4


def test_individuals_query_no_permissions(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_REQUEST_BODY)
    data = response.get_json()

    # expect normal response with zero results
    assert response.status_code == 200
    assert "responseSummary" in data
    assert data["responseSummary"]["numTotalResults"] == 0


def test_network_endpoint(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)
    response = client.get("/network")
    assert response.status_code == 200
    assert "beacons" in response.get_json()
