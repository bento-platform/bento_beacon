import json
import os
from ..utils.exceptions import APIException


class Config:
    BENTO_URL = os.environ.get("BENTOV2_PORTAL_DOMAIN", "http://127.0.0.1")

    # TODO: should default to false, not true
    DEBUG = os.environ.get("BEACON_DEBUG", True)

    # can be "boolean", "count", or "record"
    BEACON_GRANULARITY = os.environ.get("BEACON_GRANULARITY", "count")

# -------------------
# katsu

    KATSU_BASE_URL = os.environ.get(
        "KATSU_BASE_URL", "https://portal.bentov2.local/api/metadata")
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

    GOHAN_BASE_URL = os.environ.get(
        "BEACON_GOHAN_BASE_URL", "https://portal.bentov2.local/api/gohan")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_OVERVIEW_ENDPOINT = "/variants/overview"
    GOHAN_TIMEOUT = int(os.environ.get("BEACON_GOHAN_TIMEOUT", 60))

# -------------------
# handle injected config files

    def retrieve_config_json(filename):
        config_path = os.path.dirname(os.path.abspath(__file__))
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