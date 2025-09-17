from copy import deepcopy
from .data.service_responses import (
    katsu_projects_response,
    katsu_public_rules_response,
    katsu_config_search_fields_response,
    gohan_search_response,
    katsu_private_search_response,
    katsu_private_search_response_no_results,
    katsu_private_search_for_files,
    katsu_private_search_for_phenopackets,
    katsu_public_search_response,
    katsu_private_search_overview_response,
    katsu_individuals_response,
    katsu_scope_error_response,
    token_response,
    drs_query_response,
    service_down_html_response,
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


PROJECT_1 = "fake_project_123"
PROJECT_1_DATASET = "abc123"
PROJECT_2 = "fake_project_345"
PROJECT_2_DATASET = "dataset-345-01"

DATASET_SCOPED_BEACON_REQUEST_BODY = deepcopy(BEACON_REQUEST_BODY)
DATASET_SCOPED_BEACON_REQUEST_BODY["query"]["datasets"] = {"datasetIds": [PROJECT_1_DATASET]}

BEACON_TOO_MANY_DATASETS = deepcopy(BEACON_REQUEST_BODY)
BEACON_TOO_MANY_DATASETS["query"]["datasets"] = {"datasetIds": [PROJECT_1_DATASET, "a-second-dataset"]}

BEACON_FULL_RECORD_REQUEST_BODY = deepcopy(BEACON_REQUEST_BODY)
BEACON_FULL_RECORD_REQUEST_BODY["query"]["requestedGranularity"] = "record"

BEACON_BOOL_REQUEST_BODY = deepcopy(BEACON_REQUEST_BODY)
BEACON_BOOL_REQUEST_BODY["query"]["requestedGranularity"] = "boolean"

BEACON_PHENOPACKET_QUERY = deepcopy(BEACON_REQUEST_BODY)
BEACON_PHENOPACKET_QUERY["query"]["filters"] = [
    {"id": "phenopacket.diseases/term.label", "operator": "=", "value": "COVID-19"}
]


# aioresponses includes query params when matching urls
KATSU_QUERY_PARAMS = "sex=FEMALE"
KATSU_QUERY_PARAMS_PROJECT_SCOPED = f"project={PROJECT_1}&sex=FEMALE"
KATSU_QUERY_PARAMS_DATASET_SCOPED = f"dataset={PROJECT_1_DATASET}&project={PROJECT_1}&sex=FEMALE"

GOHAN_QUERY_PARAMS = "assemblyId=GRCh38&chromosome=3&getSampleIdsOnly=True&lowerBound=189631389&upperBound=189897276"

HANDOVER_FILES = [
    "HG00100.vcf.gz",
    "HG00102.vcf.gz",
]


def mock_retrieve_token(app_config, aioresponse):
    openid_config_url = app_config["OPENID_CONFIG_URL"]
    token_url = app_config["AUTHZ_URL"] + "/fake/token"
    aioresponse.get(openid_config_url, payload=TOKEN_ENDPOINT_CONFIG_RESPONSE)
    aioresponse.post(token_url, payload=token_response, repeat=True)


# checked permissions (in order):
# "query:data"
# "download:data"
# "query:project_level_counts"
# "query:project_level_boolean"
# "query:dataset_level_counts"
# "query:dataset_level_boolean"


def mock_permissions_all(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[True, True, True, True, True, True, True]]})


def mock_permissions_all_except_download(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[True, False, True, True, True, True, True]]})


def mock_permissions_none(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[False, False, False, False, False, False, False]]})


def mock_permissions_project_counts(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[False, False, True, True, True, True]]})


def mock_permissions_dataset_counts_for_non_dataset_resource(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[False, False, False, False, True, True]]})


# does not include project permissions
def mock_permissions_dataset_counts_for_dataset_resource(app_config, aioresponse):
    mock_retrieve_token(app_config, aioresponse)
    authz_evaluate_url = app_config["AUTHZ_URL"] + "/policy/evaluate"
    aioresponse.post(authz_evaluate_url, payload={"result": [[False, False, True, True]]})


def mock_katsu_public_rules(app_config, aioresponse, project_id=None, dataset_id=None):
    params = ""
    if dataset_id or project_id:
        params = "?"
        if dataset_id:
            params += f"dataset={PROJECT_1_DATASET}&"
        if project_id:
            params += f"project={PROJECT_1}"
    public_rules_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PUBLIC_RULES"] + params
    aioresponse.get(public_rules_url, payload=katsu_public_rules_response)


def mock_katsu_public_rules_mismatched_scope(app_config, aioresponse):
    mismatched_rules_url = (
        app_config["KATSU_BASE_URL"]
        + app_config["KATSU_PUBLIC_RULES"]
        + f"?dataset={PROJECT_1_DATASET}&project={PROJECT_2}"
    )
    aioresponse.get(mismatched_rules_url, payload=katsu_scope_error_response)


def mock_katsu_projects(app_config, aioresponse):
    projects_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PROJECTS_ENDPOINT"] + "?format=phenopackets"
    aioresponse.get(projects_url, payload=katsu_projects_response)


def mock_katsu_public_search_fields(app_config, aioresponse, project_id=None):
    search_fields_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PUBLIC_CONFIG_ENDPOINT"]
    if project_id:
        search_fields_url += f"?project={project_id}"
    aioresponse.get(search_fields_url, payload=katsu_config_search_fields_response)


def mock_katsu_public_search_no_query(app_config, aioresponse):
    public_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_BEACON_SEARCH"]
    aioresponse.get(public_search_url, payload=katsu_public_search_response)


def mock_katsu_public_search_query(app_config, aioresponse, query_params):
    public_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_BEACON_SEARCH"] + "?" + query_params
    aioresponse.get(public_search_url, payload=katsu_public_search_response)


def mock_katsu_private_search_query(app_config, aioresponse):
    private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    aioresponse.post(private_search_url, payload=katsu_private_search_response)


def mock_katsu_private_search_query_no_results(app_config, aioresponse):
    private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    aioresponse.post(private_search_url, payload=katsu_private_search_response_no_results)


def mock_katsu_private_search_for_handover_files(app_config, aioresponse):
    private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    aioresponse.post(private_search_url, payload=katsu_private_search_for_files)


def mock_katsu_private_search_for_phenopackets(app_config, aioresponse):
    private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    aioresponse.post(private_search_url, payload=katsu_private_search_for_phenopackets)


def mock_katsu_private_search_query_scoped(app_config, aioresponse, project_id=None, dataset_id=None):
    private_search_url = (
        app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"] + "?" + f"project={project_id}"
    )
    if dataset_id:
        private_search_url += f"&dataset={dataset_id}"
    aioresponse.post(private_search_url, payload=katsu_private_search_response)


def mock_katsu_private_search_overview(app_config, aioresponse):
    search_overview_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_OVERVIEW"]
    aioresponse.post(search_overview_url, payload=katsu_private_search_overview_response)


def mock_katsu_individuals(app_config, aioresponse):
    individuals_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_INDIVIDUALS_ENDPOINT"] + "?page_size=1"
    aioresponse.get(individuals_url, payload=katsu_individuals_response)


def mock_katsu_individuals_scoped(app_config, aioresponse):
    individuals_url = (
        app_config["KATSU_BASE_URL"] + app_config["KATSU_INDIVIDUALS_ENDPOINT"] + f"?page_size=1&project={PROJECT_1}"
    )
    aioresponse.get(individuals_url, payload=katsu_individuals_response)


def mock_gohan_overview(app_config, aioresponse):
    gohan_overview_url = app_config["GOHAN_BASE_URL"] + app_config["GOHAN_OVERVIEW_ENDPOINT"]
    aioresponse.get(gohan_overview_url, payload=gohan_search_response)


def mock_gohan_query(app_config, aioresponse):
    gohan_search_url = app_config["GOHAN_BASE_URL"] + app_config["GOHAN_SEARCH_ENDPOINT"] + "?" + GOHAN_QUERY_PARAMS
    aioresponse.get(gohan_search_url, payload=gohan_search_response)


def mock_gohan_query_client_error(aioresponse):
    bad_gohan_search_url = ""
    aioresponse.get(bad_gohan_search_url, payload={})


def mock_service_down_response(aioresponse, method, url):
    if method == "POST":
        aioresponse.post(url, status=404, body=service_down_html_response, content_type="text/html")
    if method == "GET":
        aioresponse.get(url, status=404, body=service_down_html_response, content_type="text/html")


def mock_service_empty_response(aioresponse, method, url):
    if method == "POST":
        aioresponse.post(url, payload={})
    if method == "GET":
        aioresponse.get(url, payload={})


def mock_drs_queries(app_config, aioresponse):
    for vcf in HANDOVER_FILES:
        drs_query_url = app_config["DRS_URL"] + "/search?name=" + vcf
        aioresponse.get(drs_query_url, payload=drs_query_response)


# --------------------------------------------------------
# info endpoints
# --------------------------------------------------------


def test_service_info(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)
    response = client.get("/service-info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["service-info"])


def test_service_info_scoped(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)
    response = client.get(f"/{PROJECT_1}/service-info")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["service-info"])


def test_root(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)  # scope check before request
    mock_katsu_projects(app_config, aioresponse)  # collecting dataset descriptions
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


def test_map(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)
    response = client.get("/map")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["map"])


def test_entry_types(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)
    response = client.get("/entry_types")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["entry_types"])


def test_configuration_endpoint(app_config, client, aioresponse):
    mock_katsu_projects(app_config, aioresponse)
    response = client.get("/configuration")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["configuration"])


def test_filtering_terms(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_fields(app_config, aioresponse)
    response = client.get("/filtering_terms")
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["filtering_terms"])


def test_filtering_terms_scoped(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_projects(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1)
    mock_katsu_public_search_fields(app_config, aioresponse, project_id=PROJECT_1)
    response = client.get(f"{PROJECT_1}/filtering_terms")
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
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1)
    response = client.get(f"/{PROJECT_1}/individuals")
    assert response.status_code == 200
    validate_response(response.get_json(), RESPONSE_SPEC_FILENAMES["count_response"])


# --------------------------------------------------------
# query /individuals
# --------------------------------------------------------


def test_individuals_query_all_permissions(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
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
    assert data["responseSummary"]["numTotalResults"] == 9


def test_individuals_full_record_query_all_permissions(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_for_handover_files(app_config, aioresponse)
    mock_katsu_private_search_for_phenopackets(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    mock_drs_queries(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_FULL_RECORD_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert "resultsHandovers" in data["response"]["resultSets"][PROJECT_2_DATASET]
    assert data["responseSummary"]["numTotalResults"] == 9


def test_individuals_full_record_query_all_permissions_except_download(app_config, client, aioresponse):
    mock_permissions_all_except_download(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_for_phenopackets(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    mock_drs_queries(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_FULL_RECORD_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert "resultsHandovers" not in data["response"]["resultSets"][PROJECT_2_DATASET]
    assert data["responseSummary"]["numTotalResults"] == 9


def test_individuals_boolean_query(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_for_phenopackets(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    mock_drs_queries(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_BOOL_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["exists"] == True


def test_individuals_query_project_scoped(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS_PROJECT_SCOPED)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS_PROJECT_SCOPED)
    mock_katsu_private_search_query_scoped(app_config, aioresponse, project_id=PROJECT_1)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post(f"/{PROJECT_1}/individuals", json=BEACON_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 9


def test_individuals_query_dataset_scoped(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1, dataset_id=PROJECT_1_DATASET)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS_DATASET_SCOPED)
    mock_katsu_private_search_query_scoped(app_config, aioresponse, project_id=PROJECT_1, dataset_id=PROJECT_1_DATASET)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post(f"/{PROJECT_1}/individuals", json=DATASET_SCOPED_BEACON_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 9


def test_individuals_phenopacket_query_no_katsu_results(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_private_search_query_no_results(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_PHENOPACKET_QUERY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 0


def test_individuals_query_bad_katsu_private_search_response(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    katsu_private_search_url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    mock_service_empty_response(aioresponse, "POST", katsu_private_search_url)
    mock_katsu_private_search_for_handover_files(app_config, aioresponse)
    mock_katsu_private_search_for_phenopackets(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_PHENOPACKET_QUERY)
    assert response.status_code == 500


def test_individuals_query_gohan_client_error(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query_client_error(aioresponse)
    response = client.post("/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 500


def test_individuals_query_scoped_too_many_datasets(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    response = client.post(f"/{PROJECT_1}/individuals", json=BEACON_TOO_MANY_DATASETS)
    assert response.status_code == 400


def test_individuals_query_mismatched_scope(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules_mismatched_scope(app_config, aioresponse)
    response = client.post(f"/{PROJECT_2}/individuals", json=DATASET_SCOPED_BEACON_REQUEST_BODY)

    # currently katsu 404s are obscured
    assert response.status_code == 500


def test_individuals_count_query_no_permissions(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_REQUEST_BODY)

    # expect permissions error
    assert response.status_code == 403


def test_individuals_full_record_query_no_permissions(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_FULL_RECORD_REQUEST_BODY)

    # expect permissions error
    assert response.status_code == 403


def test_individuals_bool_query_no_permissions(app_config, client, aioresponse):
    mock_permissions_none(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post("/individuals", json=BEACON_BOOL_REQUEST_BODY)

    # expect permissions error
    assert response.status_code == 403


def test_individuals_by_id_query_wrong_permissions(app_config, client, aioresponse):
    mock_permissions_project_counts(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.get("/individuals/abc123")

    # expect permissions error
    assert response.status_code == 403


# --------------------------------------------------------
# query /individuals scoped
# --------------------------------------------------------


def test_individuals_query_project_with_dataset_permissions(app_config, client, aioresponse):
    mock_permissions_dataset_counts_for_non_dataset_resource(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1)
    response = client.post(f"/{PROJECT_1}/individuals", json=BEACON_REQUEST_BODY)  # url
    data = response.get_json()

    # expect permissions error
    assert response.status_code == 403


def test_individuals_query_dataset_with_dataset_permissions(app_config, client, aioresponse):
    mock_permissions_dataset_counts_for_dataset_resource(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse, project_id=PROJECT_1, dataset_id=PROJECT_1_DATASET)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS_DATASET_SCOPED)
    mock_katsu_private_search_query_scoped(app_config, aioresponse, project_id=PROJECT_1, dataset_id=PROJECT_1_DATASET)
    mock_katsu_private_search_overview(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    response = client.post(f"/{PROJECT_1}/individuals", json=DATASET_SCOPED_BEACON_REQUEST_BODY)
    data = response.get_json()
    assert response.status_code == 200
    assert data["responseSummary"]["numTotalResults"] == 9


# --------------------------------------------------------
# handle service errors
# --------------------------------------------------------


def test_katsu_non_json_response_from_get(app_config, client, aioresponse):
    katsu_endpoint = app_config["KATSU_PROJECTS_ENDPOINT"] + "?format=phenopackets"
    url = app_config["KATSU_BASE_URL"] + app_config["KATSU_PROJECTS_ENDPOINT"] + "?format=phenopackets"
    mock_service_down_response(aioresponse, "GET", url)
    service_info_response = client.get("/service-info")
    assert service_info_response.status_code == 500


def test_katsu_non_json_response_from_post(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_gohan_query(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    url = app_config["KATSU_BASE_URL"] + app_config["KATSU_SEARCH_ENDPOINT"]
    mock_service_down_response(aioresponse, "POST", url)
    query_response = client.post("/individuals", json=BEACON_REQUEST_BODY)
    assert query_response.status_code == 500


def test_gohan_down_response(app_config, client, aioresponse):
    mock_permissions_all(app_config, aioresponse)
    mock_katsu_public_rules(app_config, aioresponse)
    mock_katsu_public_search_query(app_config, aioresponse, KATSU_QUERY_PARAMS)
    mock_katsu_private_search_query(app_config, aioresponse)
    mock_katsu_private_search_overview(app_config, aioresponse)
    url = app_config["GOHAN_BASE_URL"] + app_config["GOHAN_SEARCH_ENDPOINT"] + "?" + GOHAN_QUERY_PARAMS
    mock_service_down_response(aioresponse, "GET", url)
    response = client.post("/individuals", json=BEACON_REQUEST_BODY)
    assert response.status_code == 500
