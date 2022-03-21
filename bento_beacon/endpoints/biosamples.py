from json import JSONDecodeError
import requests
from flask import Blueprint, jsonify, current_app
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_response import beacon_response, katsu_not_found
from ..utils.katsu_queries import query_katsu
from ..utils.beacon_mappings import katsu_biosample_to_beacon_biosample

biosamples = Blueprint("biosamples", __name__, url_prefix="/api")


# TODO

@biosamples.route("/biosamples", methods=['GET', 'POST'])
def get_biosamples():
    raise NotImplemented()


@biosamples.route("/biosamples/<id>", methods=['GET', 'POST'])
def biosamples_by_id(id):
    r = get_katsu_biosamples_by_id(id)
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
    katsu_response = query_katsu(
        current_app.config["KATSU_BIOSAMPLES_ENDPOINT"], id)

    current_app.logger.info(katsu_response)

    if katsu_not_found(katsu_response):
        current_app.logger.info("katsu not found")
        return beacon_response([])

    mapped_repsonse = katsu_biosample_to_beacon_biosample(katsu_response)
    return beacon_response([mapped_repsonse])
