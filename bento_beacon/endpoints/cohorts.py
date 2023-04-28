from flask import Blueprint, current_app
from ..utils.exceptions import NotImplemented
from ..utils.beacon_response import beacon_response

cohorts = Blueprint("cohorts", __name__)


@cohorts.route("/cohorts", methods=['GET', 'POST'])
def get_cohorts():
    granularity = current_app.config["DEFAULT_GRANULARITY"]["cohorts"]

    cohort = current_app.config["BEACON_COHORT"]
    results = {"collections": cohort}
    return beacon_response(results, collection_response=True)


@cohorts.route("/cohorts/<id>", methods=['GET', 'POST'])
def get_cohort_by_id(id):
    cohort = current_app.config["BEACON_COHORT"]
    response = cohort if id == cohort.get("id") else {}
    return beacon_response(response, collection_response=True)


@cohorts.route("/cohorts/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_cohort(id):
    raise NotImplemented()


@cohorts.route("/cohorts/<id>/filtering_terms", methods=['GET', 'POST'])
def filtering_terms_by_cohort(id):
    raise NotImplemented()
