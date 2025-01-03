from flask import Blueprint, current_app
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import beacon_info_response
from ..utils.katsu_utils import (
    get_filtering_terms,
    katsu_total_individuals_count,
    katsu_get,
    katsu_datasets,
)
from ..utils.gohan_utils import gohan_counts_for_overview


info = Blueprint("info", __name__)


async def overview():
    if current_app.config["BEACON_CONFIG"].get("useGohan"):
        variants_count = await gohan_counts_for_overview()
    else:
        variants_count = {}

    return {"counts": {"individuals": await katsu_total_individuals_count(), "variants": variants_count}}


# service-info in ga4gh format
@info.route("/service-info")
@authz_middleware.deco_public_endpoint
async def service_info():
    # plain response without beacon wrappers
    return current_app.config.get("BEACON_GA4GH_SERVICE_INFO", await build_ga4gh_service_info())


# service info in beacon format
@info.route("/")
@authz_middleware.deco_public_endpoint
async def beacon_info():
    return beacon_info_response(current_app.config.get("SERVICE_DETAILS", await build_service_details()))


# as above but with beacon overview details
@info.route("/info")
@authz_middleware.deco_public_endpoint
async def beacon_info_with_overview():
    service_info = current_app.config.get("SERVICE_DETAILS", await build_service_details())
    return beacon_info_response({**service_info, "overview": await overview()})


@info.route("/filtering_terms")
@authz_middleware.deco_public_endpoint
async def filtering_terms():
    filtering_terms = await get_filtering_terms()
    return beacon_info_response({"resources": [], "filteringTerms": filtering_terms})


# distinct from "BEACON_CONFIG"
@info.route("/configuration")
@authz_middleware.deco_public_endpoint
async def beacon_configuration():
    return beacon_info_response(
        current_app.config.get("CONFIGURATION_ENDPOINT_RESPONSE", await build_configuration_endpoint_response())
    )


@info.route("/entry_types")
@authz_middleware.deco_public_endpoint
def entry_types():
    e_types = current_app.config.get("ENTRY_TYPES", build_entry_types())
    return beacon_info_response({"entryTypes": e_types})


@info.route("/map")
@authz_middleware.deco_public_endpoint
def beacon_map():
    return beacon_info_response(current_app.config.get("BEACON_MAP", build_beacon_map()))


# custom endpoint not in beacon spec
@info.route("/overview")
@authz_middleware.deco_public_endpoint
async def beacon_overview():
    service_info = current_app.config.get("SERVICE_DETAILS", await build_service_details())
    return beacon_info_response({**service_info, "overview": await overview()})


# -------------------------------------------------------
#  schemas
# -------------------------------------------------------


@info.route("/individual_schema", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint
async def get_individual_schema():
    return await katsu_get(current_app.config["KATSU_INDIVIDUAL_SCHEMA_ENDPOINT"], requires_auth="none")


@info.route("/experiment_schema", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint
async def get_experiment_schema():
    return await katsu_get(current_app.config["KATSU_EXPERIMENT_SCHEMA_ENDPOINT"], requires_auth="none")


# -------------------------------------------------------
#  utility functions for building responses
# -------------------------------------------------------
# these return the appropriate response but also save as a side effect


async def build_service_details():
    # build info response in beacon format
    info = current_app.config["BEACON_CONFIG"].get("serviceInfo")
    s = {
        "id": current_app.config["BEACON_ID"],
        "name": current_app.config["BEACON_NAME"],
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "environment": "dev" if current_app.config["DEBUG"] else "prod",
        "organization": info["organization"],
        "version": current_app.config["BENTO_BEACON_VERSION"],
    }

    # url for beacon ui
    if current_app.config["BEACON_UI_ENABLED"]:
        s["welcomeUrl"] = current_app.config["BEACON_UI_URL"]

    # retrieve dataset description from DATS
    # may be multiple datasets, so collect all descriptions into one string
    # for custom description, add a "description" field to service info in beacon_config.json
    k_datasets = await katsu_datasets()
    dats_array = list(map(lambda d: d.get("datsFile", {}), k_datasets))
    description = " ".join([d.get("description") for d in dats_array if "description" in d])
    custom_description = info.get("description")
    if custom_description:
        s["description"] = custom_description
    if description and custom_description is None:
        s["description"] = description

    current_app.config["SERVICE_DETAILS"] = s
    return s


async def build_ga4gh_service_info():
    # construct from beacon-format info
    info = current_app.config.get("SERVICE_DETAILS", await build_service_details())

    s = {
        "id": info["id"],
        "name": info["name"],
        "type": {"artifact": "Beacon v2", "group": "org.ga4gh", "version": info["apiVersion"]},
        "environment": info["environment"],
        "organization": {"name": info["organization"]["name"], "url": info["organization"].get("welcomeUrl", "")},
        "contactUrl": info["organization"]["contactUrl"],
        "version": info["version"],
        "bento": {"serviceKind": "beacon"},
    }

    description = info.get("description")
    if description:
        s["description"] = description

    current_app.config["BEACON_GA4GH_SERVICE_INFO"] = s

    return s


async def build_configuration_endpoint_response():
    entry_types_details = current_app.config.get("ENTRY_TYPES", build_entry_types())

    # production status is one of "DEV", "PROD", "TEST"
    # while environment is one of "dev", "prod", "test", "staging".. generally only use "dev" or "prod"
    production_status = (
        current_app.config.get("SERVICE_DETAILS", await build_service_details()).get("environment", "error").upper()
    )

    response = {
        "$schema": current_app.config["INFO_ENDPOINTS_SCHEMAS"]["/configuration"]["schema"],
        "entryTypes": entry_types_details,
        "maturityAttributes": {"productionStatus": production_status},
    }
    current_app.config["CONFIGURATION_ENDPOINT_RESPONSE"] = response
    return response


def build_entry_types():
    entry_types = {}
    endpoint_sets = current_app.config["BEACON_CONFIG"].get("endpointSets")
    entry_types_details = current_app.config["ENTRY_TYPES_DETAILS"]
    for endpoint_set in endpoint_sets:
        entry = entry_types_details.get(endpoint_set)
        entry_type_name = entry.get("entryType")

        entry_types[entry_type_name] = {
            "id": entry_type_name,
            "name": entry.get("name"),
            "ontologyTermForThisType": entry.get("ontologyTermForThisType"),
            "partOfSpecification": entry.get("partOfSpecification"),
            "defaultSchema": entry.get("defaultSchema"),
        }

    current_app.config["ENTRY_TYPES"] = entry_types
    return entry_types


def build_beacon_map():
    beacon_map = {"$schema": current_app.config["INFO_ENDPOINTS_SCHEMAS"]["/map"]["schema"], "endpointSets": {}}
    endpoint_sets = current_app.config["BEACON_CONFIG"].get("endpointSets")
    for endpoint_set in endpoint_sets:
        resource_name = "g_variants" if endpoint_set == "variants" else endpoint_set
        root_url = current_app.config["BEACON_BASE_URL"] + "/" + resource_name
        entry_type = current_app.config["ENTRY_TYPES_DETAILS"].get(endpoint_set, {}).get("entryType")
        beacon_map["endpointSets"][entry_type] = {"rootUrl": root_url, "entryType": entry_type}

        if endpoint_set in ["datasets", "cohorts"]:
            beacon_map["endpointSets"][entry_type]["singleEntryUrl"] = root_url + "/{id}"

    current_app.config["BEACON_MAP"] = beacon_map
    return beacon_map
