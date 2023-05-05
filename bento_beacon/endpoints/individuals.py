from flask import Blueprint
from functools import reduce
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response, add_info_to_response
from ..utils.katsu_utils import katsu_filters_and_sample_ids_query, katsu_filters_query, katsu_total_individuals_count, search_from_config
from ..utils.gohan_utils import query_gohan

individuals = Blueprint("individuals", __name__)


@individuals.route("/individuals", methods=['GET', 'POST'])
def get_individuals():
    variants_query, phenopacket_filters, experiment_filters, config_filters = query_parameters_from_request()

    # ----------------------------------------------------------
    #  collect biosample ids from variant and experiment search
    # ----------------------------------------------------------

    results_biosample_ids = {}

    # if no query, return total count of individuals
    if not (variants_query or phenopacket_filters or experiment_filters or config_filters):
        add_info_to_response("no query found, returning total count")
        total_count = katsu_total_individuals_count()
        return beacon_response({"count": total_count})

    if variants_query:
        variant_sample_ids = query_gohan(variants_query, "count", ids_only=True)
        if not variant_sample_ids:
            return beacon_response({"count": 0, "results": []})
        results_biosample_ids["variant_sample_ids"] = variant_sample_ids
    
    if experiment_filters:
        experiment_sample_ids = katsu_filters_query(experiment_filters, "experiment", get_biosample_ids=True)
        if not experiment_sample_ids:
            return beacon_response({"count": 0, "results": []})
        results_biosample_ids["experiment_sample_ids"] = experiment_sample_ids

    # compute intersection of everything in "results" dict
    # dict is either empty or has dict entries that are non-empty
    if results_biosample_ids:
        # ornate syntax but avoids a lot of separate edge cases
        sample_ids = list(reduce(set.intersection, (set(ids) for ids in results_biosample_ids.values())))
    else:
        sample_ids = []

    # -----------------------------------------------------------
    #  collect individual ids from phenopacket and config search
    # -----------------------------------------------------------

    # an alternative here is to return biosample ids from config search instead of individual ids,
    # and then move the code to the block above. But this would mean implicitly hardcoding the
    # linked field set in katsu, which we probably don't want

    results_individual_ids = {}

    # get all individuals from phenopacket search,
    # but limit results to people with matching sample ids from searches above
    phenopacket_ids = katsu_filters_and_sample_ids_query(phenopacket_filters, "phenopacket", sample_ids)
    if phenopacket_ids:
        results_individual_ids["phenopacket_ids"] = phenopacket_ids

    if config_filters:
        config_ids = search_from_config(config_filters)
        results_individual_ids["config_ids"] = config_ids
        
    if results_individual_ids:
        individual_ids = list(reduce(set.intersection, (set(ids) for ids in results_individual_ids.values())))
    else:
        individual_ids = []

    return beacon_response({"count": len(individual_ids), "results": individual_ids})


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
