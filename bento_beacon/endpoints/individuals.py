from flask import Blueprint, g
from functools import reduce
from ..authz.utils import has_download_data_permissions, requires_full_record_permissions
from ..utils.beacon_request import summary_stats_requested
from ..utils.beacon_response import (
    add_info_to_response,
    add_stats_to_response,
    add_overview_stats_to_response,
    zero_count_response,
    build_query_response,
    beacon_result_set_response,
)
from ..utils.katsu_utils import (
    katsu_filters_and_sample_ids_query,
    katsu_total_individuals_count,
    search_from_config,
    phenopackets_for_ids,
)
from ..utils.search import individuals_search_with_dnf_filters
from ..utils.handover_utils import handover_for_ids
from ..utils.exceptions import NotFoundException
from ..utils.scope import scoped_route_decorator_for_blueprint

individuals = Blueprint("individuals", __name__)
route_with_optional_project_id = scoped_route_decorator_for_blueprint(individuals)


@route_with_optional_project_id("/individuals", methods=["GET", "POST"])
async def get_individuals(project_id=None):
    variants_query = g.beacon_query["variants_query"]
    filters = g.beacon_query["filters"]

    no_query = not (variants_query or filters)
    dataset_id = g.beacon_query["dataset_id"]

    # return total count of individuals if no query
    # TODO: save 400ms on beacon UI startup by not calling katsu twice
    if no_query:
        add_info_to_response("no query found, returning total count")
        total_count = await katsu_total_individuals_count(project_id=project_id, dataset_id=dataset_id)
        if summary_stats_requested():
            await add_overview_stats_to_response(project_id=project_id, dataset_id=dataset_id)
        return await build_query_response(num_total_results=total_count)

    # ga4gh proof of concept, handle config filters only
    individual_ids = await individuals_search_with_dnf_filters(variants_query, filters, project_id, dataset_id)

    if summary_stats_requested():
        await add_stats_to_response(individual_ids, project_id, dataset_id)

    return await build_query_response(ids=individual_ids, full_record_handler=individuals_full_results)


# TODO: pagination (ideally after katsu search gets paginated)
async def individuals_full_results(ids, project_id=None, dataset_id=None):

    # temp
    # if len(ids) > 100:
    #     return {"message": "too many ids for full response"}

    handover_permission = has_download_data_permissions(g.permissions)
    handover = (await handover_for_ids(ids, project_id, dataset_id)) if handover_permission else {}
    phenopackets_by_result_set = (await phenopackets_for_ids(ids, project_id, dataset_id)).get("results", {})
    result_ids = list(phenopackets_by_result_set.keys())
    result_sets = {}
    num_total_results = 0

    for r_id in result_ids:
        results_this_id = phenopackets_by_result_set.get(r_id, {}).get("matches", [])
        results_count = len(results_this_id)
        num_total_results += results_count
        result = {
            "id": r_id,
            "setType": "individual",
            "exists": results_count > 0,
            "resultsCount": results_count,
            "results": results_this_id,
        }
        handover_this_id = handover.get(r_id, [])
        if handover_this_id:
            result["resultsHandovers"] = handover_this_id
        result_sets[r_id] = result

    return result_sets, num_total_results


# forbidden / unauthorized if no permissions
@route_with_optional_project_id("/individuals/<id>", methods=["GET", "POST"])
@requires_full_record_permissions
async def individual_by_id(id, project_id=None):
    dataset_id = g.beacon_query["dataset_id"]
    result_sets, num_total_results = await individuals_full_results([id], project_id=project_id, dataset_id=dataset_id)

    # return 404 if not found
    # only authorized users will get 404 here, so this can't be used to probe ids
    if not result_sets:
        raise NotFoundException()

    return beacon_result_set_response(result_sets, num_total_results)


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /individuals/<id>/g_variants
#           - may be simpler to download vcf instead
#       /individuals/<id>/biosamples
#           - requires full response code for biosamples (could just serve phenopackets again here)
#       /individuals/<id>/filtering_terms
#           - unclear use case, isn't reading the full response better?
#           - requires better ontology support / better filtering terms implementation
# -------------------------------------------------------
