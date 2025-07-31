from .test_routes import (
    mock_permissions_all,
    mock_katsu_public_rules,
    mock_katsu_projects,
    mock_gohan_overview,
    mock_katsu_individuals,
    mock_katsu_public_search_fields,
    mock_katsu_public_search_query,
    mock_katsu_public_search_no_query,
    mock_katsu_private_search_query,
    mock_katsu_private_search_overview,
    mock_gohan_query,
    KATSU_QUERY_PARAMS,
    BEACON_REQUEST_BODY,
)
from .data.service_responses import (
    network_beacon_overview_bento_18,
    network_beacon_query_response_bento_18,
    network_beacon_filtering_terms_response_bento_18,
)


def mock_network_beacon_overview(aioresponse):
    url = "https://fake2.bento.ca/api/beacon/overview"
    aioresponse.get(url, payload=network_beacon_overview_bento_18)


def mock_network_beacon_query_response(aioresponse):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aioresponse.post(url, payload=network_beacon_query_response_bento_18)


def mock_network_beacon_filtering_terms(aioresponse):
    url = "https://fake2.bento.ca/api/beacon/filtering_terms"
    aioresponse.get(url, payload=network_beacon_filtering_terms_response_bento_18)


def mock_network_init(app_config, aioresponse):
    mock_permissions_all(app_config, aioresponse)

    # calls to network beacons
    mock_network_beacon_overview(aioresponse)
    mock_network_beacon_filtering_terms(aioresponse)

    # calls for local beacon hosting the network
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_fields(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_gohan_overview(app_config, aioresponse)
    mock_katsu_individuals(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_public_search_no_query(app_config, aioresponse)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)


def test_network_endpoint(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    response = client.get("/network")
    assert response.status_code == 200
    assert "beacons" in response.get_json()


def test_network_config_missing(app_config, client):
    app_config["NETWORK_CONFIG"] = {}
    response = client.get("/network")
    assert response.status_code == 500


def test_network_beacon_query(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    mock_network_beacon_query_response(aioresponse)
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 200


def test_network_beacon_query_bad_endpoint(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    INCORRECT_ENDPOINT = "individualzz"
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/{INCORRECT_ENDPOINT}", json=BEACON_REQUEST_BODY)
    assert response.status_code == 404


def test_network_beacon_query_bad_http_verb(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    response = client.get(f"/network/beacons/ca.fake2.bento.beacon/individuals")
    assert response.status_code == 500

def test_network_beacon_query_bad_beacon_id(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    mock_network_beacon_query_response(aioresponse)
    INCORRECT_ID = "bad-id"
    response = client.post(f"/network/beacons/{INCORRECT_ID}/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 404


def test_network_local_beacon_query(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_network_init(app_config, aioresponse)
    response = client.post(f"/network/beacons/local.test.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 200
