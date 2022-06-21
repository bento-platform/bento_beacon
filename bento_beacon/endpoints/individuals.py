from flask import Blueprint, current_app, request

from ..utils.beacon_response import beacon_response
from ..utils.katsu_utils import katsu_filters_query
from ..utils.gohan_utils import gohan_results

individuals = Blueprint("individuals", __name__, url_prefix="/api")



@individuals.route("/individuals", methods=['GET', 'POST'])
def get_individuals():
    granularity = current_app.config["BEACON_GRANULARITY"]
    beacon_args = request.get_json() or {}

    variants_query = beacon_args.get("query", {}).get("requestParameters", {}).get("g_variant") or {} 
    filters = beacon_args.get("query", {}).get("requestParameters", {}).get("filters") or {} 
    results = {}

    # if variants query, retrieve sample ids from gohan
    # then call katsu with filters (if any) and sample ids (if any)
    # this approach requires changes to bento_lib sql generation, but eliminates joins and 
    # makes pagination easier

    if variants_query: 
        sample_ids = gohan_results(variants_query, granularity, ids_only=True)
        print(f"gohan sample ids: {sample_ids}")
  
    if filters:
        results = katsu_filters_query(filters)

    # TODO: variants_query AND filters

    return beacon_response(results)


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
