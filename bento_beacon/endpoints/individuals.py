from flask import Blueprint
from functools import reduce
from ..authz.middleware import PERMISSION_DOWNLOAD_DATA, PERMISSION_QUERY_DATA, check_permission
from ..utils.beacon_request import (
    query_parameters_from_request,
    summary_stats_requested,
    )
from ..utils.beacon_response import (
    beacon_response,
    add_info_to_response,
    add_stats_to_response,
    add_overview_stats_to_response,
    zero_count_response,
    beacon_full_response
)
from ..utils.katsu_utils import (
    katsu_filters_and_sample_ids_query,
    katsu_total_individuals_count,
    search_from_config,
    phenopackets_for_ids
)
from ..utils.search import biosample_id_search
from ..utils.handover_utils import handover_for_ids

individuals = Blueprint("individuals", __name__)


@individuals.route("/individuals", methods=['GET', 'POST'])
def get_individuals():

    full_response = check_permission(PERMISSION_QUERY_DATA)

    variants_query, phenopacket_filters, experiment_filters, config_filters = query_parameters_from_request()

    no_query = not (variants_query or phenopacket_filters or experiment_filters or config_filters)
    search_sample_ids = variants_query or experiment_filters
    config_search_only = config_filters and not (variants_query or phenopacket_filters or experiment_filters)

    # return total count of individuals if no query
    # TODO: return default granularity rather than count (default could be bool rather than count)
    if no_query:
        add_info_to_response("no query found, returning total count")
        total_count = katsu_total_individuals_count()
        if summary_stats_requested():
            add_overview_stats_to_response()
        return beacon_response({"count": total_count})

    # ----------------------------------------------------------
    #  collect biosample ids from variant and experiment search
    # ----------------------------------------------------------
    sample_ids = []

    if search_sample_ids:
        sample_ids = biosample_id_search(variants_query=variants_query, experiment_filters=experiment_filters)
        if not sample_ids:
            return zero_count_response()

    # -------------------------------
    #  get individuals
    # -------------------------------

    individual_results = {}

    # get individuals from katsu config search
    if config_filters:
        config_ids = search_from_config(config_filters)
        if not config_ids:
            return zero_count_response()
        individual_results["config_ids"] = config_ids

    if not config_search_only:
        # retrieve all matching individuals from sample id search, filtered by any phenopacket filters
        # either of phenopacket_filters or sample_ids can be empty
        phenopacket_ids = katsu_filters_and_sample_ids_query(phenopacket_filters, "phenopacket", sample_ids)
        if not phenopacket_ids:
            return zero_count_response()
        individual_results["phenopacket_ids"] = phenopacket_ids

    # baroque syntax but covers all cases
    individual_ids = list(reduce(set.intersection, (set(ids) for ids in individual_results.values())))

    # conditionally add summary statistics to response
    if summary_stats_requested():
        add_stats_to_response(individual_ids)

    if full_response:
        return individuals_full_response(individual_ids)
    
    # TODO: configurable default response rather than hardcoded counts
    return beacon_response({"count": len(individual_ids), "results": individual_ids})


# TODO: pagination (ideally after katsu search gets paginated)
def individuals_full_response(ids):

    # temp
    # if len(ids) > 100:
    #     return {"message": "too many ids for full response"}

    handover_permission = check_permission(PERMISSION_DOWNLOAD_DATA)
    handover = handover_for_ids(ids) if handover_permission else {}
    phenopackets_by_result_set = phenopackets_for_ids(ids).get("results", {})
    result_ids = list(phenopackets_by_result_set.keys())
    result_sets = {}

    for r_id in result_ids:
        results_this_id = phenopackets_by_result_set.get(r_id, {}).get("matches", [])
        results_count = len(results_this_id)
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

    return beacon_full_response(result_sets)


# -------------------------------------------------------
#       unimplemented endpoints
# -------------------------------------------------------
# these would be appropriate for full-access beacons only

# replace this one once auth is in place
# @individuals.route("/individuals/<id>", methods=['GET', 'POST'])
# @authn_token_required_flask_wrapper
# def individual_by_id(id):
#     # get one individual by id, with handover if available
#     return individuals_full_response([id])


# @individuals.route("/individuals/<id>/g_variants", methods=['GET', 'POST'])
# def individual_variants(id):
#     # all variants for a particular individual
#     # may never be implemented, bad match for our use case (download vcf instead)
#     raise NotImplemented()


# @individuals.route("/individuals/<id>/biosamples", methods=['GET', 'POST'])
# def individual_biosamples(id):
#     # all biosamples for a particular individual
#     pass


# @individuals.route("/individuals/<id>/filtering_terms", methods=['GET', 'POST'])
# def individual_filtering_terms(id):
#     # filtering terms for a particular individual
#     # note that this involves private data   
#     pass
