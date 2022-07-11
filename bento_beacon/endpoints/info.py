import os
import json
from flask import Blueprint, current_app, request
from ..utils.beacon_response import beacon_info_response


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

    # bento_beacon/beacon-framework-v2/responses/beaconFilteringTermsResponse.json
    # beacon-framework-v2/responses/sections/beaconFilteringTermsResults.json

    # see also:
    # bento_beacon/beacon-framework-v2/requests/validation/filteringTerms.json
    return {"filtering terms": "TODO"}
# "list of filtering terms"


@info.route("/configuration")
def beacon_configuration():
    return beacon_info_response(current_app.config["BEACON_CONFIGURATION"])


@info.route("/entry_types")
def entry_types():

    # bento_beacon/beacon-framework-v2/responses/beaconEntryTypesResponse.json
    # bento_beacon/beacon-framework-v2/configuration/entryTypesSchema.json
    return {"entry types": "TODO"}


@info.route("/map")
def beacon_map():
    return beacon_info_response(current_app.config["BEACON_MAP"])
