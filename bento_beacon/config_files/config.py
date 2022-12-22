import json
import os


class Config:
    # TODO: should default to false, not true
    DEBUG = os.environ.get("BEACON_DEBUG", True)

    # can be "boolean", "count", or "record"
    BEACON_GRANULARITY = os.environ.get("BEACON_GRANULARITY", "count")

    # version of ga4gh beacon spec, not version of this implementation
    BEACON_API_VERSION = "v2.0.0"

    SMALL_CELL_COUNT_THRESHOLD = os.environ.get("BEACON_SMALL_CELL_COUNT_THRESHOLD", 0)

# -------------------
# katsu

    KATSU_BASE_URL = os.environ.get("KATSU_BASE_URL")
    KATSU_BIOSAMPLES_ENDPOINT = "/api/biosamples"
    KATSU_INDIVIDUALS_ENDPOINT = "/api/individuals"
    KATSU_DATASETS_ENDPOINT = "/api/datasets"
    KATSU_SEARCH_ENDPOINT = "/private/search"
    KATSU_RESOURCES_ENDPOINT = "/api/resources"
    KATSU_PHENOTYPIC_FEATURE_TERMS_ENDPOINT = "/api/phenotypic_feature_type_autocomplete"
    KATSU_DISEASES_TERMS_ENDPOINT = "/api/disease_term_autocomplete"
    KATSU_SAMPLED_TISSUES_TERMS_ENDPOINT = "/api/biosample_sampled_tissue_autocomplete"
    KATSU_TIMEOUT = int(os.environ.get("BEACON_KATSU_TIMEOUT", 180))

    MAP_EXTRA_PROPERTIES_TO_INFO = os.environ.get(
        "MAP_EXTRA_PROPERTIES_TO_INFO", True)

# -------------------
# gohan

    GOHAN_BASE_URL = os.environ.get("GOHAN_BASE_URL")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_OVERVIEW_ENDPOINT = "/variants/overview"
    GOHAN_TIMEOUT = int(os.environ.get("BEACON_GOHAN_TIMEOUT", 60))

# -------------------
# handle injected config files
#   a) obtain reference to the expected configuration files' location by
#      using the programmable env variable `CONFIG_ABSOLUTE_PATH` if it exists, or
#   b) default to using "this file's directory" as the reference to where
#      configuration files are expected to be located
    def retrieve_config_json(filename):
        # TODO: abstract out CONFIG_PATH if needed
        config_path = os.environ.get("CONFIG_ABSOLUTE_PATH", os.path.dirname(os.path.abspath(__file__)))
        print(f"Searching for file {filename} in {config_path}")
        file_path = os.path.join(config_path, filename)
        try:
            with open(file_path) as f:
                data = json.load(f)
                return data    
        except FileNotFoundError:
            # TODO: proper error response           
            return {"message": "Beacon error, missing config file"}    

    BEACON_SERVICE_INFO = retrieve_config_json("beacon_service_info.json")

    BEACON_CONFIGURATION = retrieve_config_json("beacon_configuration.json")

    # TODO: correct paths with BENTO_URL
    BEACON_MAP = retrieve_config_json("beacon_map.json")

    # TODO: parameterize, merge with beacon service info
    BEACON_GA4GH_SERVICE_INFO = retrieve_config_json("beacon_ga4gh_service_info.json")

    BEACON_ENDPOINTS = retrieve_config_json("beacon_endpoints.json")

    BEACON_COHORT = retrieve_config_json("beacon_cohort.json")