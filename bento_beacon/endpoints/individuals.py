from flask import Blueprint, current_app, g
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response, add_info_to_response, beacon_response_with_handover
from ..utils.katsu_utils import katsu_filters_and_sample_ids_query, katsu_filters_query, katsu_total_individuals_count, phenopackets_for_ids
from ..utils.gohan_utils import query_gohan
from ..utils.handover_utils import handover_for_ids

from bento_lib.auth.wrappers import authn_token_required_flask_wrapper, authn_token_optional_flask_wrapper

individuals = Blueprint("individuals", __name__)


# TODO: pagination
# total count of responses available at katsu_results.count
# call and return phenopacket and handover results in batches
def individuals_full_response(ids):

    # temp
    # if len(ids) > 100:
    #     return {"message": "too many ids for full response"}

    handover = handover_for_ids(ids)
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

    return beacon_response_with_handover(result_sets)


@individuals.route("/individuals", methods=['GET', 'POST'])
@authn_token_optional_flask_wrapper
def get_individuals():
    auth_enabled = current_app.authx['enabled']
    has_valid_token = "authn" in g and g.authn.get("has_valid_token", False)
    private = auth_enabled and has_valid_token

    # TODO: data access filtering by roles
    # if current_app.authx['enabled']:
    #     print(g.authn['roles'])

    variants_query, phenopacket_filters, experiment_filters = query_parameters_from_request()

    # if no query, return total count of individuals
    if not (variants_query or phenopacket_filters or experiment_filters):
        add_info_to_response("no query found, returning total count")
        total_count = katsu_total_individuals_count()
        return beacon_response({"count": total_count})

    if variants_query:
        variant_sample_ids = query_gohan(variants_query, "count", ids_only=True)
        if not variant_sample_ids:
            return beacon_response({"count": 0, "results": []})
    
    if experiment_filters:
        experiment_sample_ids = katsu_filters_query(experiment_filters, "experiment", get_biosample_ids=True)
        if not experiment_sample_ids:
            return beacon_response({"count": 0, "results": []})

    # compute cases for results
    # some redundant bools for clarity
    sample_ids = []
    if variants_query and experiment_filters:
        sample_ids = list(set(variant_sample_ids) & set(experiment_sample_ids))
        if not sample_ids:
            return beacon_response({"count": 0, "results": []})
    if variants_query and not experiment_filters:
        sample_ids = variant_sample_ids
    if experiment_filters and not variants_query:
        sample_ids = experiment_sample_ids

    # finally, get all matching individuals
    phenopacket_results = katsu_filters_and_sample_ids_query(phenopacket_filters, "phenopacket", sample_ids)

    if private and phenopacket_results:
        return individuals_full_response(phenopacket_results)
    else:
        return beacon_response({"count": len(phenopacket_results), "results": phenopacket_results})



@individuals.route("/individuals/<id>", methods=['GET', 'POST'])
@authn_token_required_flask_wrapper
def individual_by_id(id):
    # get one individual by id
    return {"individual by id": "TODO"}


@individuals.route("/individuals/<id>/g_variants", methods=['GET', 'POST'])
def individual_variants(id):
    # all variants for a particular individual
    return {"individual variants": "TODO"}


@individuals.route("/individuals/<id>/biosamples", methods=['GET', 'POST'])
def individual_biosamples(id):
    # all biosamples for a particular individual
    return {"individual biosamples": "TODO"}


@individuals.route("/individuals/<id>/filtering_terms", methods=['GET', 'POST'])
def individual_filtering_terms(id):
    # filtering terms for a particular individual
    return {"individual filtering terms": "TODO"}
