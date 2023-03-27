from flask import Blueprint, current_app
from ..utils.beacon_response import beacon_info_response
from ..utils.katsu_utils import get_filtering_terms, get_filtering_term_resources, katsu_total_individuals_count
from ..utils.gohan_utils import gohan_assembly_ids, gohan_total_variants_count


info = Blueprint("info", __name__)


def overview():
    return {
        "assemblyIds": gohan_assembly_ids(),
        "counts":
        {
            "individuals": katsu_total_individuals_count(),
            "variants": gohan_total_variants_count()
        }
    }


# service-info in ga4gh format
@info.route("/service-info")
def service_info():
    return current_app.config["BEACON_GA4GH_SERVICE_INFO"]


# service info in beacon format
@info.route("/")
def beacon_info():
    return beacon_info_response(current_app.config["BEACON_SERVICE_INFO"])


# as above but with beacon overview details
@info.route("/info")
def beacon_info_with_overview():
    return beacon_info_response({**current_app.config["BEACON_SERVICE_INFO"], "overview": overview()})


@info.route("/filtering_terms")
def filtering_terms():
    resources = get_filtering_term_resources()
    filtering_terms = get_filtering_terms()
    return beacon_info_response({"resources": resources, "filteringTerms": filtering_terms})


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
