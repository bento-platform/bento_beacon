from .test_routes import (
    mock_permissions_none,
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
)
from .data.service_responses import (
    network_beacon_overview_bento_17,
    network_beacon_overview_bento_18,
    network_beacon_query_response_bento_17,
    network_beacon_query_response_bento_18,
    katsu_config_search_fields_response,
    network_beacon_overview_bento_18_with_pr_build,
)


def mock_network_beacon_bento_17_overview(aioresponse):
    url = "https://fake1.bento.ca/api/beacon/overview"
    aioresponse.get(url, payload=network_beacon_overview_bento_17)


def mock_network_beacon_bento_18_overview(aioresponse):
    url = "https://fake2.bento.ca/api/beacon/overview"
    aioresponse.get(url, payload=network_beacon_overview_bento_18)


def mock_network_beacon_bento_18_overview_from_pr_build(aioresponse):
    url = "https://fake-patched.bento.ca/api/beacon/overview"
    aioresponse.get(url, payload=network_beacon_overview_bento_18_with_pr_build)


def mock_network_beacon_bento_17_query_response(aioresponse):
    url = "https://fake1.bento.ca/api/beacon/individuals"
    aioresponse.post(url, payload=network_beacon_query_response_bento_17)


def mock_network_beacon_bento_18_query_response(aioresponse):
    url = "https://fake2.bento.ca/api/beacon/individuals"
    aioresponse.post(url, payload=network_beacon_query_response_bento_18)


def mock_network_beacon_bento_18_query_response_from_pr_build(aioresponse):
    url = "https://fake-patched.bento.ca/api/beacon/individuals"
    aioresponse.post(url, payload=network_beacon_query_response_bento_18)


def mock_network_katsu_public_fields_response_bento_17(aioresponse):
    url = "https://portal.fake1.bento.ca/api/metadata/api/public_search_fields"
    aioresponse.get(url, payload=katsu_config_search_fields_response)


def mock_network_katsu_public_fields_response_bento_18(aioresponse):
    url = "https://fake2.bento.ca/api/metadata/api/public_search_fields"
    aioresponse.get(url, payload=katsu_config_search_fields_response)


def mock_network_katsu_public_fields_response_bento_18_from_pr_build(aioresponse):
    url = "https://fake-patched.bento.ca/api/metadata/api/public_search_fields"
    aioresponse.get(url, payload=katsu_config_search_fields_response)


def test_network_endpoint(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)

    # calls to network beacons
    mock_network_beacon_bento_17_overview(aioresponse)
    mock_network_beacon_bento_18_overview(aioresponse)
    mock_network_beacon_bento_18_overview_from_pr_build(aioresponse)
    mock_network_beacon_bento_17_query_response(aioresponse)
    mock_network_beacon_bento_18_query_response(aioresponse)
    mock_network_beacon_bento_18_query_response_from_pr_build(aioresponse)

    # calls to network katsus
    mock_network_katsu_public_fields_response_bento_17(aioresponse)
    mock_network_katsu_public_fields_response_bento_18(aioresponse)
    mock_network_katsu_public_fields_response_bento_18_from_pr_build(aioresponse)

    # calls for local beacon hosting the network
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_fields(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_gohan_overview(app_config, aioresponse)
    mock_katsu_individuals(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse)
    mock_katsu_public_search_no_query(app_config, aioresponse)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)

    response = client.get("/network")
    assert response.status_code == 200
    assert "beacons" in response.get_json()
