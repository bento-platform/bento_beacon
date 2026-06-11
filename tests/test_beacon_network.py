from aiohttp import ClientConnectionError

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
    network_beacon_filtering_terms_response_has_no_overlap_with_other_beacons,
    network_beacon_bad_discovery_key_response,
    network_beacon_bad_discovery_value_response,
)


def mock_network_beacon_overview(aio):
    url = "https://fake2.bento.ca/api/beacon/overview"
    aio.get(url, payload=network_beacon_overview_bento_18)


def mock_network_beacon_query_response(aio):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aio.post(url, payload=network_beacon_query_response_bento_18)


def mock_network_beacon_query_throws_exception(aio):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aio.post(url, payload=network_beacon_query_response_bento_18, exception=ClientConnectionError("Connection refused"))


def mock_network_beacon_query_bad_discovery_key(aio):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aio.post(url, status=400, payload=network_beacon_bad_discovery_key_response)


def mock_network_beacon_query_bad_discovery_value(aio):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aio.post(url, status=400, payload=network_beacon_bad_discovery_value_response)


def mock_network_beacon_filtering_terms(aio):
    url = "https://fake2.bento.ca/api/beacon/filtering_terms"
    aio.get(url, payload=network_beacon_filtering_terms_response_bento_18)


def mock_network_beacon_filtering_terms_beacon_down(aio):
    url = "https://fake2.bento.ca/api/beacon/filtering_terms"
    aio.get(url, status=404)


def mock_network_beacon_filtering_terms_empty(aio):
    url = "https://fake2.bento.ca/api/beacon/filtering_terms"
    aio.get(url, payload={"response": {"filtering_terms": []}})


def mock_network_beacon_filtering_terms_with_one_weird_field(aio):
    url = "https://fake2.bento.ca/api/beacon/filtering_terms"
    aio.get(url, payload=network_beacon_filtering_terms_response_has_no_overlap_with_other_beacons)


def mock_local_beacon_init_calls(app_config, aio):
    mock_katsu_public_rules(app_config, aio)
    mock_katsu_public_search_fields(app_config, aio)
    mock_katsu_projects(app_config, aio)
    mock_gohan_overview(app_config, aio)
    mock_katsu_individuals(app_config, aio)
    mock_katsu_public_search_query(app_config, aio, KATSU_QUERY_PARAMS)
    mock_katsu_public_search_no_query(app_config, aio)
    mock_katsu_private_search_query(app_config, aio)
    mock_katsu_private_search_overview(app_config, aio)
    mock_gohan_query(app_config, aio)


def mock_network_init(app_config, aio):
    mock_permissions_all(app_config, aio)

    # calls to network beacons
    mock_network_beacon_overview(aio)
    mock_network_beacon_filtering_terms(aio)

    # calls for local beacon hosting the network
    mock_local_beacon_init_calls(app_config, aio)


def mock_network_init_bad_filtering_terms(app_config, aio):
    mock_permissions_all(app_config, aio)

    # calls to network beacons
    mock_network_beacon_overview(aio)
    mock_network_beacon_filtering_terms_beacon_down(aio)

    # calls for local beacon hosting the network
    mock_local_beacon_init_calls(app_config, aio)


def mock_network_init_empty_filtering_terms(app_config, aio):
    mock_permissions_all(app_config, aio)

    # calls to network beacons
    mock_network_beacon_overview(aio)
    mock_network_beacon_filtering_terms_empty(aio)

    # calls for local beacon hosting the network
    mock_local_beacon_init_calls(app_config, aio)


def mock_network_init_filtering_terms_with_empty_intersection(app_config, aio):
    mock_permissions_all(app_config, aio)

    # calls to network beacons
    mock_network_beacon_overview(aio)
    mock_network_beacon_filtering_terms_with_one_weird_field(aio)

    # calls for local beacon hosting the network
    mock_local_beacon_init_calls(app_config, aio)


def test_network_endpoint(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    response = client.get("/network")
    assert response.status_code == 200
    assert "beacons" in response.get_json()


def test_network_config_missing(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    network_config = app_config["NETWORK_CONFIG"]
    app_config["NETWORK_CONFIG"] = {}
    response = client.get("/network")
    assert response.status_code == 500
    # replace config or we kill the other tests
    app_config["NETWORK_CONFIG"] = network_config


def test_network_beacon_query(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    mock_network_beacon_query_response(aio)
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 200


def test_network_beacon_query_failed(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    mock_network_beacon_query_throws_exception(aio)
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 500


def test_network_beacon_query_bad_discovery_key(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    mock_network_beacon_query_bad_discovery_key(aio)
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 400
    error_message = response.get_json().get("error", {}).get("errorMessage")
    assert "Query used an unsupported filter" in error_message


def test_network_beacon_query_bad_discovery_value(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    mock_network_beacon_query_bad_discovery_value(aio)
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 400
    error_message = response.get_json().get("error", {}).get("errorMessage")
    assert "Query used an unsupported filter" in error_message


def test_network_beacon_query_bad_endpoint(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    INCORRECT_ENDPOINT = "individualzz"
    response = client.post(f"/network/beacons/ca.fake2.bento.beacon/{INCORRECT_ENDPOINT}", json=BEACON_REQUEST_BODY)
    assert response.status_code == 404


def test_network_beacon_query_bad_http_verb(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    response = client.get(f"/network/beacons/ca.fake2.bento.beacon/individuals")
    assert response.status_code == 501


def test_network_beacon_query_bad_beacon_id(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    mock_network_beacon_query_response(aio)
    INCORRECT_ID = "bad-id"
    response = client.post(f"/network/beacons/{INCORRECT_ID}/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 404


def test_network_local_beacon_query(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init(app_config, aio)
    response = client.post(f"/network/beacons/local.test.beacon/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 200


def test_network_beacon_bad_filtering_terms_call(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init_bad_filtering_terms(app_config, aio)
    response = client.get("/network")
    # still expect OK response
    assert response.status_code == 200
    assert "beacons" in response.get_json()


def test_network_beacon_with_no_filter_intersection(app_config, client, aio):
    mock_permissions_all(app_config, aio)
    mock_network_init_filtering_terms_with_empty_intersection(app_config, aio)
    response = client.get("/network")
    assert response.status_code == 200
    assert "beacons" in response.get_json()
