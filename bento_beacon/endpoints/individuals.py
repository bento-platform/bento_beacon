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
from ..utils.search import biosample_id_search
from ..utils.handover_utils import handover_for_ids
from ..utils.exceptions import NotFoundException, PermissionsException
from ..utils.scope import scoped_route_decorator_for_blueprint

individuals = Blueprint("individuals", __name__)
route_with_optional_project_id = scoped_route_decorator_for_blueprint(individuals)


@route_with_optional_project_id("/individuals", methods=["GET", "POST"])
async def get_individuals(project_id=None):
    variants_query = g.beacon_query["variants_query"]
    phenopacket_filters = g.beacon_query["phenopacket_filters"]
    experiment_filters = g.beacon_query["experiment_filters"]
    config_filters = g.beacon_query["config_filters"]
    dataset_id = g.beacon_query["dataset_id"]

    no_query = not (variants_query or phenopacket_filters or experiment_filters or config_filters)
    search_sample_ids = variants_query or experiment_filters
    config_search_only = config_filters and not (variants_query or phenopacket_filters or experiment_filters)

    # return total count of individuals if no query
    # TODO: save 400ms on beacon UI startup by not calling katsu twice
    if no_query:
        add_info_to_response("no query found, returning total count")
        total_count = await katsu_total_individuals_count(project_id=project_id, dataset_id=dataset_id)
        if summary_stats_requested():
            await add_overview_stats_to_response(project_id=project_id, dataset_id=dataset_id)
        return await build_query_response(numTotalResults=total_count)

    # ----------------------------------------------------------
    #  collect biosample ids from variant and experiment search
    # ----------------------------------------------------------
    sample_ids = []

    if search_sample_ids:
        sample_ids = await biosample_id_search(
            variants_query=variants_query,
            experiment_filters=experiment_filters,
            project_id=project_id,
            dataset_id=dataset_id,
        )
        if not sample_ids:
            return await zero_count_response()

    # -------------------------------
    #  get individuals
    # -------------------------------

    individual_results = {}

    # get individuals from katsu config search
    if config_filters:
        config_ids = await search_from_config(config_filters, project_id=project_id, dataset_id=dataset_id)
        if not config_ids:
            return await zero_count_response()
        individual_results["config_ids"] = config_ids

    if not config_search_only:
        # retrieve all matching individuals from sample id search, filtered by any phenopacket filters
        # either of phenopacket_filters or sample_ids can be empty
        phenopacket_ids = await katsu_filters_and_sample_ids_query(
            phenopacket_filters, "phenopacket", sample_ids, project_id=project_id, dataset_id=dataset_id
        )
        if not phenopacket_ids:
            return await zero_count_response()
        individual_results["phenopacket_ids"] = phenopacket_ids

    # baroque syntax but covers all cases
    individual_ids = list(reduce(set.intersection, (set(ids) for ids in individual_results.values())))

    if summary_stats_requested():
        await add_stats_to_response(individual_ids)

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
    numTotalResults = 0

    for r_id in result_ids:
        results_this_id = phenopackets_by_result_set.get(r_id, {}).get("matches", [])
        results_count = len(results_this_id)
        numTotalResults += results_count
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

    return result_sets, numTotalResults


# forbidden / unauthorized if no permissions
@route_with_optional_project_id("/individuals/<id>", methods=["GET", "POST"])
# replaces "deco_require_permissions_on_resource" decorator, which is difficult to modify from default "everything" scope
@requires_full_record_permissions
async def individual_by_id(id, project_id=None):

    # or use this permissions check if you don't like the decorator
    # if not has_full_record_permissions(g.permissions):
    #     raise PermissionsException()

    dataset_id = g.beacon_query["dataset_id"]
    result_sets, numTotalResults = await individuals_full_results([id], project_id=project_id, dataset_id=dataset_id)

    # return 404 if not found
    # only authorized users will get 404 here, so this can't be used to probe ids
    if not result_sets:
        raise NotFoundException()

    return beacon_result_set_response(result_sets, numTotalResults)


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
