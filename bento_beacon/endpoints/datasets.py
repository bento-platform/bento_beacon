from flask import Blueprint, jsonify, current_app
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_response import beacon_response, katsu_not_found
from ..utils.katsu_utils import katsu_datasets
from ..utils.beacon_mappings import katsu_to_beacon_dataset_mapping

datasets = Blueprint("datasets", __name__, url_prefix="/api")


@datasets.route("/datasets", methods=['GET', 'POST'])
def get_datasets():
    k_datasets = katsu_datasets()
    datasets_beacon_format = list(map(katsu_to_beacon_dataset_mapping, k_datasets))
    results = {"collections": datasets_beacon_format}
    return beacon_response(results, collection_response=True)


@datasets.route("/datasets/<id>", methods=['GET', 'POST'])
def get_datasets_by_id(id):
    k_dataset = katsu_datasets(id)
    dataset_beacon_format = katsu_to_beacon_dataset_mapping(k_dataset) if k_dataset else {}
    return beacon_response(dataset_beacon_format, collection_response=True)


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