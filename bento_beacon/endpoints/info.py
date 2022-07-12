import os
import json
from flask import Blueprint, current_app, request
from ..utils.beacon_response import beacon_info_response
from ..utils.katsu_utils import get_filtering_terms, get_filtering_term_resources

# TODO: return real service info


info = Blueprint("info", __name__, url_prefix="/api")


# service-info in ga4gh format
@info.route("/service-info")
def service_info():
    config = current_app.config
    return beacon_info_response(current_app.config["BEACON_GA4GH_SERVICE_INFO"], build_meta=False)


# service info in beacon format
@info.route("/")
@info.route("/info")
def beacon_info():
    return beacon_info_response(current_app.config["BEACON_SERVICE_INFO"])


@info.route("/filtering_terms")
def filtering_terms():
    resources = get_filtering_term_resources()
    filtering_terms = get_filtering_terms()
    return beacon_info_response({"resources": resources, "filtering_terms": filtering_terms})


@info.route("/configuration")
def beacon_configuration():
    return beacon_info_response(current_app.config["BEACON_CONFIGURATION"])


@info.route("/entry_types")
def entry_types():
    entry_types = current_app.config["BEACON_CONFIGURATION"].get("entryTypes")
    return beacon_info_response({"entryTypes": entry_types})


@info.route("/map")
def beacon_map():
    return beacon_info_response(current_app.config["BEACON_MAP"])
