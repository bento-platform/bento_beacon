import json
import logging
import os
from ..constants import GRANULARITY_COUNT, GRANULARITY_RECORD
from .. import __version__


GA4GH_BEACON_REPO_URL = "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2"


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "t", "yes")


def reverse_domain_id(domain):
    return ".".join(reversed(domain.split("."))) + ".beacon"


BENTO_DEBUG = str_to_bool(os.environ.get("BENTO_DEBUG", os.environ.get("FLASK_DEBUG", "false")))

# silence logspam
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("aiocache").setLevel(logging.WARNING)


class Config:
    BEACON_SPEC_VERSION = "v2.1.1"

    # default when no requested granularity, as well as max granularity for anonymous users
    # no granularity for info endpoints
    DEFAULT_GRANULARITY = {
        "individuals": GRANULARITY_COUNT,
        "variants": GRANULARITY_COUNT,
        "biosamples": GRANULARITY_COUNT,
        "cohorts": GRANULARITY_RECORD,
        "datasets": GRANULARITY_RECORD,
        "network": GRANULARITY_COUNT,
    }

    DEFAULT_PAGINATION_PAGE_SIZE = 10

    BENTO_DEBUG = BENTO_DEBUG
    BENTO_DOMAIN = os.environ.get("BENTOV2_DOMAIN")
    BEACON_BASE_URL = os.environ.get("BEACON_BASE_URL")
    BENTO_PUBLIC_URL = os.environ.get("BENTOV2_PUBLIC_URL")
    BEACON_ID = reverse_domain_id(BENTO_DOMAIN)
    BEACON_NAME = os.environ.get("BENTO_PUBLIC_CLIENT_NAME", "Bento") + " Beacon"
    BEACON_UI_ENABLED = str_to_bool(os.environ.get("BENTO_BEACON_UI_ENABLED", ""))
    BEACON_UI_URL = BENTO_PUBLIC_URL + "/#/en/beacon"

    ENTRY_TYPES_DETAILS = {
        "biosamples": {
            "entryType": "biosample",
            "name": "Biosample",
            "ontologyTermForThisType": {"id": "NCIT:C70699", "label": "Biospecimen"},
            "defaultSchema": {
                "id": f"ga4gh-beacon-biosample-{BEACON_SPEC_VERSION}",
                "name": "Default schema for biosamples",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/biosamples/defaultSchema.json",
                "schemaVersion": BEACON_SPEC_VERSION,
            },
            "partOfSpecification": f"Beacon {BEACON_SPEC_VERSION}",
        },
        "cohorts": {
            "entryType": "cohort",
            "name": "Cohort",
            "ontologyTermForThisType": {"id": "NCIT:C61512", "label": "Cohort"},
            "defaultSchema": {
                "id": f"ga4gh-beacon-cohort-{BEACON_SPEC_VERSION}",
                "name": "Default schema for cohorts",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/cohorts/defaultSchema.json",
                "schemaVersion": BEACON_SPEC_VERSION,
            },
            "partOfSpecification": f"Beacon {BEACON_SPEC_VERSION}",
        },
        "datasets": {
            "entryType": "dataset",
            "name": "Dataset",
            "ontologyTermForThisType": {"id": "NCIT:C47824", "label": "Data set"},
            "defaultSchema": {
                "id": f"ga4gh-beacon-dataset-{BEACON_SPEC_VERSION}",
                "name": "Default schema for datasets",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/datasets/defaultSchema.json",
                "schemaVersion": BEACON_SPEC_VERSION,
            },
            "partOfSpecification": f"Beacon {BEACON_SPEC_VERSION}",
        },
        "individuals": {
            "entryType": "individual",
            "name": "Individual",
            "ontologyTermForThisType": {"id": "NCIT:C25190", "label": "Person"},
            "defaultSchema": {
                "id": "phenopacket-v2",
                "name": "phenopacket v2",
                "referenceToSchemaDefinition": f"{BEACON_BASE_URL}/individual_schema",
                "schemaVersion": BEACON_SPEC_VERSION,
            },
            "partOfSpecification": "Phenopacket v2",
        },
        "variants": {
            "entryType": "genomicVariation",
            "name": "Genomic Variant",
            "ontologyTermForThisType": {"id": "ENSGLOSSARY:0000092", "label": "Variant"},
            "defaultSchema": {
                "id": f"ga4gh-beacon-variant-{BEACON_SPEC_VERSION}",
                "name": "Default schema for a genomic variation",
                "referenceToSchemaDefinition": f"{GA4GH_BEACON_REPO_URL}/main/models/json/beacon-v2-default-model/genomicVariations/defaultSchema.json",
                "schemaVersion": BEACON_SPEC_VERSION,
            },
            "partOfSpecification": f"Beacon {BEACON_SPEC_VERSION}",
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
    KATSU_PROJECTS_ENDPOINT = "/api/projects"
    KATSU_DATASETS_ENDPOINT = "/api/datasets"
    KATSU_SEARCH_ENDPOINT = "/private/search"
    KATSU_RESOURCES_ENDPOINT = "/api/resources"
    KATSU_PUBLIC_CONFIG_ENDPOINT = "/api/public_search_fields"
    KATSU_INDIVIDUAL_SCHEMA_ENDPOINT = "/api/schemas/phenopacket"
    KATSU_EXPERIMENT_SCHEMA_ENDPOINT = "/api/schemas/experiment"
    KATSU_BEACON_SEARCH = "/api/public"
    KATSU_SEARCH_OVERVIEW = "/api/search_overview"
    KATSU_PUBLIC_OVERVIEW = "/api/public_overview"
    KATSU_PUBLIC_RULES = "/api/public_rules"
    KATSU_TIMEOUT = int(os.environ.get("BEACON_KATSU_TIMEOUT", 180))

    MAP_EXTRA_PROPERTIES_TO_INFO = str_to_bool(os.environ.get("MAP_EXTRA_PROPERTIES_TO_INFO", ""))

    MAX_RETRIES_FOR_CENSORSHIP_PARAMS = int(os.environ.get("MAX_RETRIES_FOR_CENSORSHIP_PARAMS", 2))

    # don't allow queries over arbitrary phenopacket or experiment fields without permission
    CENSORED_METADATA_QUERY_USES_DISCOVERY_CONFIG_ONLY = True

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
    # reference
    REFERENCE_URL = os.environ.get("REFERENCE_URL")

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

    # -------------------
    # network

    USE_BEACON_NETWORK = os.environ.get("BENTO_BEACON_NETWORK_ENABLED", "false").strip().lower() in ("true", "1", "t")

    NETWORK_CONFIG = retrieve_config_json("beacon_network_config.json")

    NETWORK_URLS = NETWORK_CONFIG.get("beacons", [])
    NETWORK_DEFAULT_TIMEOUT_SECONDS = NETWORK_CONFIG.get("network_default_timeout_seconds", 30)
    NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS = NETWORK_CONFIG.get("network_variants_query_timeout_seconds", GOHAN_TIMEOUT)
    NETWORK_VALID_QUERY_ENDPOINTS = [
        "analyses",
        "biosamples",
        "cohorts",
        "datasets",
        "g_variants",
        "individuals",
        "runs",
    ]
