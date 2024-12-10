from flask import Blueprint, current_app
from ..authz.middleware import authz_middleware
from .info import beacon_format_service_details 
from ..utils.beacon_response import beacon_info_response, add_info_to_response, summary_stats
from ..utils.katsu_utils import (
    get_filtering_terms,
    katsu_total_individuals_count,
)
from ..utils.gohan_utils import gohan_counts_for_overview
from ..utils.scope import scoped_route_decorator_for_blueprint


info_permissions_required = Blueprint("info_permissions_required", __name__)
route_with_optional_project_id = scoped_route_decorator_for_blueprint(info_permissions_required)


@route_with_optional_project_id("/info")
@authz_middleware.deco_public_endpoint
async def beacon_info_with_overview(project_id=None):
    """
    as above but with beacon overview details
    unscoped, overview details currently node-level only
    """

    service_info = await beacon_format_service_details(project_id)
    return beacon_info_response({**service_info, "overview": await overview()})


@route_with_optional_project_id("/overview")
@authz_middleware.deco_public_endpoint
async def beacon_overview(project_id=None):
    """
    Custom endpoint not in beacon spec
    currently node-level overview only 
    """
    service_info = await beacon_format_service_details(project_id)
    return beacon_info_response({**service_info, "overview": await overview(project_id)})


# xxxxxxxxxxxxxxxx move this to its own blueprint, since this now looks at permissions xxxxxxxxxxxxxxxxx
# could be scoped by dataset only by adding query params for dataset (endpoint is GET only)
# this endpoint normally doesn't take queries at all, the only params it recognizes are for pagination
# could also annotating filtering terms with a dataset id in cases where it's limited to a particular dataset
@route_with_optional_project_id("/filtering_terms")
@authz_middleware.deco_public_endpoint
async def filtering_terms(project_id=None):
    """
    response scoped by project.
    could be scoped by dataset by adding query params
    but this endpoint isn't meant to accept queries, the only params it recognizes are for pagination
    """
    filtering_terms = await get_filtering_terms(project_id)
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

    # can be removed once bento_public is updated (it reads from counts.variants for assemblyIDs)
    legacy_format_overview = {"counts": {"individuals": await katsu_total_individuals_count(), "variants": variants}}

    katsu_stats = await summary_stats(None)
    beacon_overview = {"variants": variants, **katsu_stats}

    return {**legacy_format_overview, **beacon_overview}

