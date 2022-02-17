from json import JSONDecodeError
import requests
from flask import Blueprint, jsonify, current_app
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_response import beacon_response
from ..utils.katsu_queries import query_katsu

biosamples = Blueprint("biosamples", __name__, url_prefix="/api")


# TODO

@biosamples.route("/biosamples", methods=['GET', 'POST'])
def get_biosamples():
    raise NotImplemented()

@biosamples.route("/biosamples/<id>", methods=['GET', 'POST'])
def biosamples_by_id(id):
    r=get_katsu_biosamples_by_id(id)
    return r

@biosamples.route("/biosamples/<id>/g_variants", methods=['GET', 'POST'])
def variants_by_biosample(id):
    raise NotImplemented()

@biosamples.route("/biosamples/<id>/analyses", methods=['GET', 'POST'])
def analyses_by_biosample(id):
    raise NotImplemented()

@biosamples.route("/biosamples/<id>/runs", methods=['GET', 'POST'])
def runs_by_biosample(id):
    raise NotImplemented()


# katsu GET /biosamples/{id} optional params (all strings):
# individual, procedure, is_control_sample, description, sampled_tissue, taxonomy, histological_diagnosis, tumor_progression, tumor_grade, extra_properties

def get_katsu_biosamples_by_id(id):
    katsu_response = query_katsu(current_app.config["KATSU_BIOSAMPLES_ENDPOINT"], id)

    # TODO: error handling, not found handling
    return beacon_response(katsu_response)

