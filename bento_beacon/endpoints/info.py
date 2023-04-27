from flask import Blueprint, current_app
from ..utils.beacon_response import beacon_info_response
from ..utils.katsu_utils import get_filtering_terms, get_filtering_term_resources, katsu_total_individuals_count
from ..utils.gohan_utils import gohan_counts_by_assembly_id


info = Blueprint("info", __name__)


JSON_SCHEMA = "https://json-schema.org/draft/2020-12/schema"


def overview():
    if current_app.config["BEACON_CONFIG"].get("useGohan"):
        variants_count = gohan_counts_by_assembly_id()
    else:
        variants_count = {}

    return {
        "counts": {
            "individuals": katsu_total_individuals_count(),
            "variants": variants_count
        }
    }


# service-info in ga4gh format
@info.route("/service-info")
def service_info():
    return getattr(current_app.config, "BEACON_GA4GH_SERVICE_INFO", build_ga4gh_service_info())


# service info in beacon format
@info.route("/")
def beacon_info():
    return current_app.config["BEACON_CONFIG"].get("serviceInfo")


# as above but with beacon overview details
@info.route("/info")
def beacon_info_with_overview():
    return beacon_info_response({**current_app.config["BEACON_CONFIG"].get("serviceInfo"), "overview": overview()})


@info.route("/filtering_terms")
# TODO
def filtering_terms():
    resources = get_filtering_term_resources()
    filtering_terms = get_filtering_terms()
    return beacon_info_response({"resources": resources, "filteringTerms": filtering_terms})


# distinct from "BEACON_CONFIG"
@info.route("/configuration")
def beacon_configuration():
    return current_app.config.get("CONFIGURATION_ENDPOINT_RESPONSE", build_configuration_endpoint_response())


@info.route("/entry_types")
def entry_types():
    return current_app.config.get("ENTRY_TYPES", build_entry_types())


@info.route("/map")
def beacon_map():
    return current_app.config.get("BEACON_MAP", build_beacon_map())


# -------------------------------------------------------

# utility functions for building responses
# these return the appropriate response but also save as a side effect


def build_ga4gh_service_info():
    service_info = current_app.config["BEACON_CONFIG"].get("serviceInfo")
    service_info["type"] = {
        "artifact": "Beacon v2",
        "group": "org.ga4gh",
        "version": current_app.config["BEACON_SPEC_VERSION"]
    }
    service_info["version"] = current_app.config["BENTO_BEACON_VERSION"]
    service_info["bento"] = {"serviceKind": "beacon"}
    current_app.config["BEACON_GA4GH_SERVICE_INFO"] = service_info
    return service_info


def build_configuration_endpoint_response():
    entry_types_details = current_app.config.get("ENTRY_TYPES", build_entry_types())

    # production status is one of "DEV", "PROD", "TEST"
    # while environment is one of "dev", "prod", "test", "staging".. generally only need "dev" and "prod"
    production_status = current_app.config["BEACON_CONFIG"].get("serviceInfo", {}).get("environment", "error").upper()

    response = {
        "$schema": JSON_SCHEMA,
        "entryTypes": entry_types_details,
        "maturityAttributes": {"productionStatus": production_status}
    }
    current_app.config["CONFIGURATION_ENDPOINT_RESPONSE"] = response
    return response


def build_entry_types():
    entry_types_response = {}
    endpoint_sets = current_app.config["BEACON_CONFIG"].get("endpointSets")
    entry_types_details = current_app.config["ENTRY_TYPES_DETAILS"]
    for endpoint_set in endpoint_sets:
        entry = entry_types_details.get(endpoint_set)
        entry_type_name = entry.get("entryType")

        entry_types_response[entry_type_name] = {
            "id": entry_type_name,
            "name": entry.get("name"),
            "ontologyTermForThisType": entry.get("ontologyTermForThisType"),
            "partOfSpecification": entry.get("partOfSpecification"),
            "defaultSchema": entry.get("defaultSchema")
        }

    current_app.config["ENTRY_TYPES"] = entry_types_response
    return entry_types_response


def build_beacon_map():
    beacon_map = {}
    endpoint_sets = current_app.config["BEACON_CONFIG"].get("endpointSets")
    for endpoint_set in endpoint_sets:
        resource_name = "g_variants" if endpoint_set == "variants" else endpoint_set
        root_url = current_app.config["BEACON_BASE_URL"] + "/" + resource_name
        entry_type = current_app.config["ENTRY_TYPES_DETAILS"].get(endpoint_set, {}).get("entryType")
        beacon_map[entry_type] = {"rootUrl": root_url, "entryType": entry_type}

    current_app.config["BEACON_MAP"] = beacon_map
    return beacon_map
