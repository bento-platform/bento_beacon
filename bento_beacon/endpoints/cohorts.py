from flask import Blueprint, current_app
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import beacon_collections_response

cohorts = Blueprint("cohorts", __name__)


@cohorts.route("/cohorts", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint
def get_cohorts():
    cohorts = current_app.config["BEACON_COHORT"]
    return beacon_collections_response({"collections": cohorts})


@cohorts.route("/cohorts/<id>", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint
def get_cohort_by_id(id):
    cohorts = current_app.config["BEACON_COHORT"]
    cohort_this_id = next((c for c in cohorts if c.get("id") == id), [])
    return beacon_collections_response({"collections": cohort_this_id})


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /cohorts/<id>/individuals
#       /cohorts/<id>/filtering_terms
# -------------------------------------------------------
