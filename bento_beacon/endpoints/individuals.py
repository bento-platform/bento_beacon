from flask import Blueprint, current_app, g
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response, add_info_to_response, beacon_response_with_handover
from ..utils.katsu_utils import katsu_filters_and_sample_ids_query, katsu_filters_query, katsu_total_individuals_count, phenopackets_for_ids
from ..utils.gohan_utils import query_gohan
from ..utils.handover_utils import handover_for_ids

from bento_lib.auth.wrappers import authn_token_required_flask_wrapper, authn_token_optional_flask_wrapper

individuals = Blueprint("individuals", __name__)

# valid token: full record response
# no token: count response
# invalid token: http 401


# TODO: pagination
# total count of responses available at katsu_results.count
# call and return phenopacket and handover results in batches
def individuals_full_response(ids):

    # temp
    if len(ids) > 100:
        return {"message": "too many ids for full response"}

    phenopackets = phenopackets_for_ids(ids)
    handover = handover_for_ids(ids)
    return beacon_response_with_handover(phenopackets, handover)


# ugly parallel logic for both count and full-record responses
# optimised for response time rather than code beauty
@individuals.route("/individuals", methods=['GET', 'POST'])
@authn_token_optional_flask_wrapper
def get_individuals():
    auth_enabled = current_app.authx['enabled']
    has_valid_token = "authn" in g and g.authn.get("has_valid_token", False)
    private = auth_enabled and has_valid_token

    # TODO: data access filtering by roles
    # if current_app.authx['enabled']:
    #     print(g.authn['roles'])

    variants_query, filters = query_parameters_from_request()

    # if no query, return total count of individuals
    if not (variants_query or filters):
        add_info_to_response("no query found, returning total count")
        total_count = katsu_total_individuals_count()
        return beacon_response({"count": total_count})

    if variants_query:
        sample_ids = query_gohan(variants_query, "count", ids_only=True)

        # skip katsu call if no results
        if not sample_ids:
            return beacon_response({"count": 0, "results": []})
        
        katsu_results = katsu_filters_and_sample_ids_query(filters, sample_ids)

        if private:
            return individuals_full_response(katsu_results["results"])
        else:
            return beacon_response(katsu_results)

    # else filters query only
    katsu_results = katsu_filters_query(filters)
    results_ids = katsu_results["results"]

    if private and results_ids:
        return individuals_full_response(katsu_results["results"])
    else:
        return beacon_response(katsu_results)


@authn_token_required_flask_wrapper
@individuals.route("/individuals/<id>", methods=['GET', 'POST'])
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
