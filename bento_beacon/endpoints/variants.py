from flask import Blueprint, current_app, request
from ..utils.beacon_response import beacon_response
from ..utils.gohan_utils import query_gohan, gohan_total_variants_count, gohan_totals_by_sample_id
from ..utils.katsu_utils import katsu_filters_query
from ..utils.exceptions import NotImplemented

variants = Blueprint("variants", __name__)


@variants.route("/g_variants", methods=['GET', 'POST'])
def get_variants():
    granularity = current_app.config["BEACON_GRANULARITY"]
    beacon_args = request.get_json() or {}
    
    variants_query = beacon_args.get("query", {}).get("requestParameters", {}).get("g_variant") or {}
    filters = beacon_args.get("query", {}).get("filters") or []
    katsu_response_ids = []

    if filters: 
        katsu_response_ids = katsu_filters_query(filters).get("results") or []

    # if no query, return total count of variants
    if not (variants_query or filters):
        total_count = gohan_total_variants_count()
        return beacon_response({"count": total_count})

    # filters only, use sum total counts for ids 
    if (filters and not variants_query):
        totals_by_id = gohan_totals_by_sample_id()

        # temp fix for casing issues in gohan
        katsu_response_ids_lower = [id.lower() for id in katsu_response_ids]

        intersection = list(set(totals_by_id.keys()) & set(katsu_response_ids_lower))
        total_variants_count = sum(totals_by_id.get(id) for id in intersection)
        return beacon_response({"count": total_variants_count})

    # only variants query, use gohan count endpoint
    if (variants_query and not filters):
        gohan_response = query_gohan(variants_query, granularity, ids_only=False)
        gohan_response_count = gohan_response.get("count") or 0
        return beacon_response({"count": gohan_response_count})

    # else variants query and filters
    gohan_response = query_gohan(variants_query, "record", ids_only=False)
    filtered_response = list(filter(lambda c: c.get("sample_id") in katsu_response_ids, gohan_response))
    return beacon_response({"count": len(filtered_response)})


# -------------------------------------------------------
#       "by id" endpoints 
# -------------------------------------------------------
# 
# These aren't useful for a counts-only beacon (you will never know any ids)

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
