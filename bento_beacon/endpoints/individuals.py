from bento_lib.auth.permissions import (
    P_DOWNLOAD_DATA,
    P_QUERY_DATA,
)
from flask import Blueprint
from functools import reduce
from ..authz.middleware import authz_middleware, check_permission
from ..utils.beacon_request import (
    query_parameters_from_request,
    summary_stats_requested,
)
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
from ..utils.exceptions import NotFoundException

individuals = Blueprint("individuals", __name__)


@individuals.route("/individuals", methods=["GET", "POST"])
def get_individuals():
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
        return build_query_response(numTotalResults=total_count)

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

    if summary_stats_requested():
        add_stats_to_response(individual_ids)

    return build_query_response(ids=individual_ids, full_record_handler=individuals_full_results)


# TODO: pagination (ideally after katsu search gets paginated)
def individuals_full_results(ids):

    # temp
    # if len(ids) > 100:
    #     return {"message": "too many ids for full response"}

    handover_permission = check_permission(P_DOWNLOAD_DATA)
    handover = handover_for_ids(ids) if handover_permission else {}
    phenopackets_by_result_set = phenopackets_for_ids(ids).get("results", {})
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
@individuals.route("/individuals/<id>", methods=["GET", "POST"])
@authz_middleware.deco_require_permissions_on_resource({P_QUERY_DATA})
def individual_by_id(id):
    result_sets, numTotalResults = individuals_full_results([id])

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
