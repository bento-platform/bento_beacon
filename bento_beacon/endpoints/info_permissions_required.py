from flask import Blueprint, current_app, g
from ..authz.middleware import authz_middleware
from .info import beacon_format_service_details
from ..utils.beacon_response import beacon_info_response, add_info_to_response, summary_stats
from ..utils.katsu_utils import (
    get_filtering_terms,
    katsu_total_individuals_count,
)
from ..utils.gohan_utils import gohan_counts_for_overview
from ..utils.scope import scoped_route_decorator_for_blueprint
from ..utils.exceptions import InvalidQuery

info_permissions_required = Blueprint("info_permissions_required", __name__)
route_with_optional_project_id = scoped_route_decorator_for_blueprint(info_permissions_required)


@route_with_optional_project_id("/info")
async def beacon_info_with_overview(project_id=None):
    """
    Returns same beacon-format service info served from root endpoint, but with an overview added.
    overview is unscoped, no overview info is returned for scoped requests
    description field is scoped (this is pulled from datasets data)
    """
    service_info = await beacon_format_service_details(project_id)
    return beacon_info_response({**service_info, "overview": await overview(project_id)})


@route_with_optional_project_id("/overview")
async def beacon_overview(project_id=None):
    """
    Custom endpoint not in beacon spec
    currently node-level overview only
    """
    service_info = await beacon_format_service_details(project_id)
    return beacon_info_response({**service_info, "overview": await overview(project_id)})


@route_with_optional_project_id("/filtering_terms")
@authz_middleware.deco_public_endpoint
async def filtering_terms(project_id=None):
    """
    Filtering terms for single node, single project or single dataset
    Could be generalized to arbitrary datatsets, but this reflects the current restrictions in katsu and the UI
    """
    dataset_id = g.beacon_query.get("dataset_id")
    filtering_terms = await get_filtering_terms(project_id, dataset_id)
    return beacon_info_response({"resources": [], "filteringTerms": filtering_terms})


# -------------------------------------------------------
#
# -------------------------------------------------------


async def overview(project_id=None, dataset_id=None):

    # TEMP: show node-level overview only, since gohan is essentially unscoped
    # note that most overview information is currently unused
    # any overview information shown in the UI is instead driven by queries, including empty ones for node-level data
    if project_id is not None or dataset_id is not None:
        add_info_to_response("overviews scoped by project or dataset are not available")
        return {}

    if current_app.config["BEACON_CONFIG"].get("useGohan"):
        variants = await gohan_counts_for_overview()
    else:
        variants = {}

    # can be removed once bento_public and beacon network nodes are updated (it reads from counts.variants for assemblyIDs)
    legacy_format_overview = {"counts": {"individuals": await katsu_total_individuals_count(), "variants": variants}}

    katsu_stats = await summary_stats(None)
    beacon_overview = {"variants": variants, **katsu_stats}

    return {**legacy_format_overview, **beacon_overview}
