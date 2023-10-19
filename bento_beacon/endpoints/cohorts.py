from flask import Blueprint, current_app
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import beacon_collections_response

cohorts = Blueprint("cohorts", __name__)

# may need minor refactoring in the future if we use mulitple cohorts

@cohorts.route("/cohorts", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint
def get_cohorts():
    cohort = current_app.config["BEACON_COHORT"]
    return beacon_collections_response({"collections": cohort})


@cohorts.route("/cohorts/<id>", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint
def get_cohort_by_id(id):
    cohort = current_app.config["BEACON_COHORT"]
    cohort_this_id = cohort if id == cohort.get("id") else []
    return beacon_collections_response({"collections": cohort_this_id})


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /cohorts/<id>/individuals
#       /cohorts/<id>/filtering_terms
# -------------------------------------------------------
