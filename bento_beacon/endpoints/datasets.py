from flask import Blueprint
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import beacon_collections_response
from ..utils.katsu_utils import katsu_datasets, katsu_dataset_by_id
from ..utils.beacon_mappings import katsu_to_beacon_dataset_mapping
from ..utils.scope import scoped_route_decorator_for_blueprint

datasets = Blueprint("datasets", __name__)
route_with_optional_project_id = scoped_route_decorator_for_blueprint(datasets)


@route_with_optional_project_id("/datasets", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint  # TODO: authz - more flexibility in what is visible (?)
async def get_datasets(project_id=None):
    k_datasets = await katsu_datasets(project_id=project_id)
    datasets_beacon_format = list(map(katsu_to_beacon_dataset_mapping, k_datasets))
    return beacon_collections_response({"collections": datasets_beacon_format})


@route_with_optional_project_id("/datasets/<id>", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint  # TODO: authz - more flexibility in what is visible (?)
async def get_datasets_by_id(id, project_id=None):
    k_dataset = await katsu_dataset_by_id(id=id)
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
