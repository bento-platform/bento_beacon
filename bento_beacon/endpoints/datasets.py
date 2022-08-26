
from flask import Blueprint, jsonify, current_app
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_response import beacon_response, katsu_not_found
from ..utils.katsu_utils import query_katsu

datasets = Blueprint("datasets", __name__, url_prefix="/api")

@datasets.route("/datasets", methods=['GET', 'POST'])
def get_datasets():
    # TODO
    raise NotImplemented()


@datasets.route("/datasets/<id>", methods=['GET', 'POST'])
def get_datasets_by_id(id):
    raise NotImplemented()


@datasets.route("/datasets/<id>/g_variants", methods=['GET', 'POST'])
def variants_by_dataset(id):
    raise NotImplemented()


@datasets.route("/datasets/<id>/biosamples", methods=['GET', 'POST'])
def biosamples_by_dataset(id):
    raise NotImplemented()


@datasets.route("/datasets/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_dataset(id):
    raise NotImplemented()

@datasets.route("/datasets/<id>/filtering_terms", methods=['GET', 'POST'])
def filtering_terms_by_dataset(id):
    raise NotImplemented()