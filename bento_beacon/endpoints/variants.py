from flask import Blueprint, g
from ..authz.middleware import authz_middleware
from ..utils.beacon_response import build_query_response, add_info_to_response, zero_count_response
from ..utils.gohan_utils import query_gohan, gohan_total_variants_count, gohan_totals_by_sample_id
from ..utils.search import biosample_id_search

variants = Blueprint("variants", __name__)
# variant routes are not scoped, since gohan does not accept scoped queries.


# returns count or boolean only
@variants.route("/g_variants", methods=["GET", "POST"])
@authz_middleware.deco_public_endpoint  # TODO: for now. eventually, return more depending on permissions
async def get_variants():
    variants_query = g.beacon_query["variants_query"]
    phenopacket_filters = g.beacon_query["phenopacket_filters"]
    experiment_filters = g.beacon_query["experiment_filters"]
    config_filters = g.beacon_query["config_filters"]
    has_filters = phenopacket_filters or experiment_filters or config_filters

    # if no query, return total count of variants
    if not (variants_query or has_filters):
        add_info_to_response("no query found, returning total count")
        total_count = await gohan_total_variants_count()
        return await build_query_response(numTotalResults=total_count)

    #  collect biosample ids from all filters
    sample_ids = []

    if has_filters:
        sample_ids = await biosample_id_search(
            phenopacket_filters=phenopacket_filters,
            experiment_filters=experiment_filters,
            config_filters=config_filters,
        )
        if not sample_ids:
            return await zero_count_response()

    # finally, find relevant variants, depending on whether a variants query was made
    if variants_query:
        # gohan search returns uppercase only
        sample_ids = [id.upper() for id in sample_ids]

        variant_results = await query_gohan(variants_query, "record", ids_only=False)
        if has_filters:
            variant_results_list = list(filter(lambda v: v.get("sample_id") in sample_ids, variant_results))
            gohan_count = len(variant_results_list)
        else: 
            gohan_count = len(variant_results)
    else:
        # gohan overview returns lowercase only
        sample_ids = [id.lower() for id in sample_ids]

        variant_totals = await gohan_totals_by_sample_id()
        if has_filters:
            gohan_count = sum(variant_totals.get(id) for id in sample_ids if id in variant_totals)
        else:
            gohan_count = sum(variant_totals.values())

    return await build_query_response(numTotalResults=gohan_count)


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /g_variants/<id>
#       /g_variants/<id>/biosamples
#       /g_variants/<id>/individuals
#
#       ... "id" here appears to be a unique id for each entry, not a variant identifier like a dbSNP entry
# -------------------------------------------------------
