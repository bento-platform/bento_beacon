from flask import Blueprint, jsonify, current_app
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_response import beacon_response, katsu_not_found
from ..utils.katsu_utils import query_katsu

cohorts = Blueprint("cohorts", __name__, url_prefix="/api")


@cohorts.route("/cohorts", methods=['GET', 'POST'])
def get_cohorts():
    # TODO
    raise NotImplemented()


@cohorts.route("/cohorts/<id>", methods=['GET', 'POST'])
def get_cohort_by_id(id):
    raise NotImplemented()


@cohorts.route("/cohorts/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_cohort(id):
    raise NotImplemented()


@cohorts.route("/cohorts/<id>/filtering_terms", methods=['GET', 'POST'])
def filtering_terms_by_cohort(id):
    raise NotImplemented()