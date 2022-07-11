import os
import json
from flask import Blueprint, current_app, request
from ..utils.beacon_response import beacon_info_response
from ..utils.katsu_utils import get_filtering_terms, get_filtering_term_resources

# TODO: return real service info


info = Blueprint("info", __name__, url_prefix="/api")


# ga4gh service-info


@info.route("/service-info")
def service_info():
    config = current_app.config
    # TODO build and return ga4gh service info
    # https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/ga4gh-service-info-1-0-0-schema.json
    return {"service info": "TODO"}


# service info in beacon format
@info.route("/")
@info.route("/info")
def beacon_info():

    # service info in beacon format, can also return ga4gh format if query has "ga4gh-service-info-v1.0" as requested schema

    # bento_beacon/beacon-framework-v2/responses/beaconInfoResponse.json
    # bento_beacon/beacon-framework-v2/responses/sections/beaconInfoResults.json
    return {"beacon info": "TODO"}


@info.route("/filtering_terms")
def filtering_terms():
    resources = get_filtering_term_resources()
    filtering_terms = get_filtering_terms()
    return beacon_info_response({"resources": resources, "filtering_terms": filtering_terms})
# "list of filtering terms"


@info.route("/configuration")
def beacon_configuration():
    return beacon_info_response(current_app.config["BEACON_CONFIGURATION"])


@info.route("/entry_types")
def entry_types():
    entry_types = current_app.config["BEACON_CONFIGURATION"].get("entryTypes")
    return beacon_info_response({"entry_types": entry_types})


@info.route("/map")
def beacon_map():
    return beacon_info_response(current_app.config["BEACON_MAP"])
