import requests
from flask import Blueprint, jsonify, current_app, request

from ..utils.beacon_response import beacon_response
from ..utils.gohan_utils import query_gohan, gohan_total_variants_count
from ..utils.exceptions import NotImplemented

variants = Blueprint("variants", __name__, url_prefix="/api")


@variants.route("/g_variants", methods=['GET', 'POST'])
def get_variants():
    granularity = current_app.config["BEACON_GRANULARITY"]
    beacon_args = request.get_json() or {}
    
    variants_query = beacon_args.get("query", {}).get("requestParameters", {}).get("g_variant") or {}
    filters = beacon_args.get("query", {}).get("filters") or []

    # if no query, return total count of variants
    if not (variants_query or filters):
        total_count = gohan_total_variants_count()
        return beacon_response({"count": total_count})



    # TODO: if filtering terms present, call katsu and join
    # TODO: if no query, call gohan for full count of variants
    results = query_gohan(variants_query, granularity)

    return beacon_response(results)


@variants.route("/g_variants/<id>", methods=['GET', 'POST'])
def variant_by_id(id):
    # get one variant by (internal) id
    raise NotImplemented()


@variants.route("/g_variants/<id>/biosamples", methods=['GET', 'POST'])
def biosamples_by_variant(id):
    # all biosamples for a particular variant
    raise NotImplemented()


@variants.route("/g_variants/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_variant(id):
    # all individuals for a particular variant
    raise NotImplemented()
