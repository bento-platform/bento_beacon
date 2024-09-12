import json
import os
import urllib3


GA4GH_BEACON_REPO_URL = "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2"


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "t", "yes")


DEBUG = str_to_bool(os.environ.get("BENTO_DEBUG", os.environ.get("FLASK_DEBUG", "false")))
VALIDATE_SSL = str_to_bool(os.environ.get("BENTO_VALIDATE_SSL", str(not DEBUG)))

if not VALIDATE_SSL:
    # Don't let urllib3 spam us with SSL validation warnings if we're operating with SSL validation off, most likely in
    # a development/test context where we're using self-signed certificates.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Config:
    BEACON_SPEC_VERSION = "v2.0.0"

    # version of this implementation
    BENTO_BEACON_VERSION = os.environ.get("BENTO_BEACON_VERSION")

    # default when no requested granularity, as well as max granularity for anonymous users
    DEFAULT_GRANULARITY = {
        "individuals": "count",
        "variants": "count",
        "biosamples": "count",
        "cohorts": "record",
        "datasets": "record",
        "info": "record",
    }

    DEFAULT_PAGINATION_PAGE_SIZE = 10

    BENTO_DEBUG = DEBUG
    BENTO_VALIDATE_SSL = VALIDATE_SSL

    BENTO_DOMAIN = os.environ.get("BENTOV2_DOMAIN")
    BEACON_BASE_URL = os.environ.get("BEACON_BASE_URL")
    BENTO_PUBLIC_URL = os.environ.get("BENTOV2_PUBLIC_URL")

    # reverse domain id
    BEACON_ID = ".".join(reversed(BENTO_DOMAIN.split("."))) + ".beacon"

    BEACON_NAME = os.environ.get("BENTO_PUBLIC_CLIENT_NAME", "Bento") + " Beacon"
    BEACON_UI_ENABLED = str_to_bool(os.environ.get("BENTO_BEACON_UI_ENABLED", ""))
    BEACON_UI_URL = BENTO_PUBLIC_URL + "/#/en/beacon"

    ENTRY_TYPES_DETAILS = {
        "biosamples": {
            "entryType": "biosample",
            "name": "Biosample",
            "ontologyTermForThisType": {"id": "NCIT:C70699", "label": "Biospecimen"},
            "defaultSchema": {
                "id": "ga4gh-beacon-biosample-v2.0.0",
                "name": "Default schema for biosamples",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/biosamples/defaultSchema.json",
                "schemaVersion": "v2.0.0",
            },
            "partOfSpecification": "Beacon v2.0.0",
        },
        "cohorts": {
            "entryType": "cohort",
            "name": "Cohort",
            "ontologyTermForThisType": {"id": "NCIT:C61512", "label": "Cohort"},
            "defaultSchema": {
                "id": "ga4gh-beacon-cohort-v2.0.0",
                "name": "Default schema for cohorts",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/cohorts/defaultSchema.json",
                "schemaVersion": "v2.0.0",
            },
            "partOfSpecification": "Beacon v2.0.0",
        },
        "datasets": {
            "entryType": "dataset",
            "name": "Dataset",
            "ontologyTermForThisType": {"id": "NCIT:C47824", "label": "Data set"},
            "defaultSchema": {
                "id": "ga4gh-beacon-dataset-v2.0.0",
                "name": "Default schema for datasets",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/datasets/defaultSchema.json",
                "schemaVersion": "v2.0.0",
            },
            "partOfSpecification": "Beacon v2.0.0",
        },
        "individuals": {
            "entryType": "individual",
            "name": "Individual",
            "ontologyTermForThisType": {"id": "NCIT:C25190", "label": "Person"},
            "defaultSchema": {
                "id": "phenopacket-v2",
                "name": "phenopacket v2",
                "referenceToSchemaDefinition": f"{BEACON_BASE_URL}/individual_schema",
                "schemaVersion": "v2.0.0",
            },
            "partOfSpecification": "Phenopacket v2",
        },
        "variants": {
            "entryType": "genomicVariation",
            "name": "Genomic Variant",
            "ontologyTermForThisType": {"id": "ENSGLOSSARY:0000092", "label": "Variant"},
            "defaultSchema": {
                "id": "ga4gh-beacon-variant-v2.0.0",
                "name": "Default schema for a genomic variation",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/genomicVariations/defaultSchema.json",
                "schemaVersion": "v2.0.0",
            },
            "partOfSpecification": "Beacon v2.0.0",
        },
    }

    INFO_ENDPOINTS_SCHEMAS = {
        "/": {
            "entityType": "info",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconInfoResponse.json",
        },
        "/configuration": {
            "entityType": "configuration",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconConfigurationResponse.json",
        },
        "/entry_types": {
            "entityType": "entryType",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconEntryTypesResponse.json",
        },
        "/filtering_terms": {
            "entityType": "filteringTerm",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconFilteringTermsResponse.json",
        },
        "/info": {
            "entityType": "info",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconInfoResponse.json",
        },
        "/map": {
            "entityType": "map",
            "schema": f"{GA4GH_BEACON_REPO_URL}/main/framework/json/responses/beaconMapResponse.json",
        },
        "/overview": {},
    }
    # -------------------
    # katsu

    KATSU_BASE_URL = os.environ.get("KATSU_BASE_URL")
    KATSU_BIOSAMPLES_ENDPOINT = "/api/biosamples"
    KATSU_INDIVIDUALS_ENDPOINT = "/api/individuals"
    KATSU_BATCH_INDIVIDUALS_ENDPOINT = "/api/batch/individuals"
    KATSU_DATASETS_ENDPOINT = "/api/datasets"
    KATSU_SEARCH_ENDPOINT = "/private/search"
    KATSU_RESOURCES_ENDPOINT = "/api/resources"
    KATSU_PHENOTYPIC_FEATURE_TERMS_ENDPOINT = "/api/phenotypic_feature_type_autocomplete"
    KATSU_DISEASES_TERMS_ENDPOINT = "/api/disease_term_autocomplete"
    KATSU_SAMPLED_TISSUES_TERMS_ENDPOINT = "/api/biosample_sampled_tissue_autocomplete"
    KATSU_PUBLIC_CONFIG_ENDPOINT = "/api/public_search_fields"
    KATSU_INDIVIDUAL_SCHEMA_ENDPOINT = "/api/schemas/phenopacket"
    KATSU_EXPERIMENT_SCHEMA_ENDPOINT = "/api/schemas/experiment"
    KATSU_BEACON_SEARCH = "/api/public"
    KATSU_SEARCH_OVERVIEW = "/api/search_overview"
    KATSU_PRIVATE_OVERVIEW = "/api/overview"
    KATSU_PUBLIC_OVERVIEW = "/api/public_overview"
    KATSU_PUBLIC_RULES = "/api/public_rules"
    KATSU_TIMEOUT = int(os.environ.get("BEACON_KATSU_TIMEOUT", 180))

    MAP_EXTRA_PROPERTIES_TO_INFO = str_to_bool(os.environ.get("MAP_EXTRA_PROPERTIES_TO_INFO", ""))

    PHENOPACKETS_SCHEMA_REFERENCE = {"entityType": "individual", "schema": "phenopackets v1"}

    MAX_RETRIES_FOR_CENSORSHIP_PARAMS = 2
    # -------------------
    # gohan

    GOHAN_BASE_URL = os.environ.get("GOHAN_BASE_URL")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_OVERVIEW_ENDPOINT = "/variants/overview"
    GOHAN_TIMEOUT = int(os.environ.get("BEACON_GOHAN_TIMEOUT", 60))

    # -------------------
    # drs

    DRS_URL = os.environ.get("DRS_URL")

    # -------------------
    # authorization

    #  - for contacting the Bento authorization service
    AUTHZ_URL: str = os.environ.get("BENTO_AUTHZ_SERVICE_URL", "")
    AUTHZ_ENABLED: bool = str_to_bool(os.environ.get("AUTHZ_ENABLED", "true"))
    #  - for retrieving a token from an OAuth2 IdP in order to make authorized requests to Katsu
    #     --> if this is disabled, <Authorization: ...> headers from the requestor will be forwarded instead.
    AUTHZ_BENTO_REQUESTS_ENABLED: bool = str_to_bool(os.environ.get("BEACON_AUTHZ_BENTO_REQUESTS_ENABLED", "true"))
    OPENID_CONFIG_URL: str = os.environ.get("BENTO_OPENID_CONFIG_URL", "")
    CLIENT_ID: str = os.environ.get("BEACON_CLIENT_ID", "")
    CLIENT_SECRET: str = os.environ.get("BEACON_CLIENT_SECRET", "")

    # -------------------
    # handle injected config files
    #   a) obtain reference to the expected configuration files' location by
    #      using the programmable env variable `CONFIG_ABSOLUTE_PATH` if it exists, or
    #   b) default to using "this file's directory" as the reference to where
    #      configuration files are expected to be located
    @staticmethod
    def retrieve_config_json(filename):
        # TODO: abstract out CONFIG_PATH if needed
        config_path = os.environ.get("CONFIG_ABSOLUTE_PATH", os.path.dirname(os.path.abspath(__file__)))
        print(f"Searching for file {filename} in {config_path}")
        file_path = os.path.join(config_path, filename)
        try:
            with open(file_path) as f:
                data = json.load(f)
                return data
        except FileNotFoundError as e:
            # print() since flask logging won't work here
            print(f"File not found: {filename}")

            # config file not optional
            if filename == "beacon_config.json":
                raise e

            # else optional cohort file missing, error only shows if /cohorts endpoint present
            return {"message": "Beacon error, missing config file"}

    BEACON_COHORT = retrieve_config_json("beacon_cohort.json")

    BEACON_CONFIG = retrieve_config_json("beacon_config.json")
