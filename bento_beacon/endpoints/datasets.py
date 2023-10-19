from flask import Blueprint
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import beacon_collections_response
from ..utils.katsu_utils import katsu_datasets
from ..utils.beacon_mappings import katsu_to_beacon_dataset_mapping

datasets = Blueprint("datasets", __name__)


@datasets.route("/datasets", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint  # TODO: authz - more flexibility in what is visible (?)
def get_datasets():
    k_datasets = katsu_datasets()
    datasets_beacon_format = list(map(katsu_to_beacon_dataset_mapping, k_datasets))
    return beacon_collections_response({"collections": datasets_beacon_format})


@datasets.route("/datasets/<id>", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint  # TODO: authz - more flexibility in what is visible (?)
def get_datasets_by_id(id):
    k_dataset = katsu_datasets(id)
    dataset_beacon_format = katsu_to_beacon_dataset_mapping(k_dataset) if k_dataset else []
    return beacon_collections_response({"collections": dataset_beacon_format})


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /datasets/<id>/g_variants
#       /datasets/<id>/biosamples
#       /datasets/<id>/individuals
#       /datasets/<id>/filtering_terms
# ---------------------------------------------------
