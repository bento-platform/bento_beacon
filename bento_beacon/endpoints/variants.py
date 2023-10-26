from flask import Blueprint
from ..authz.middleware import authz_middleware
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import build_query_response, add_info_to_response, zero_count_response
from ..utils.gohan_utils import query_gohan, gohan_total_variants_count, gohan_totals_by_sample_id
from ..utils.search import biosample_id_search
from ..utils.exceptions import NotImplemented

variants = Blueprint("variants", __name__)


# returns count or boolean only
@variants.route("/g_variants", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint  # TODO: for now. eventually, return more depending on permissions
def get_variants():
    variants_query, phenopacket_filters, experiment_filters, config_filters = query_parameters_from_request()
    has_filters = phenopacket_filters or experiment_filters or config_filters

    # if no query, return total count of variants
    if not (variants_query or has_filters):
        add_info_to_response("no query found, returning total count")
        total_count = gohan_total_variants_count()
        return build_query_response(numTotalResults=total_count)

    #  collect biosample ids from all filters
    sample_ids = []

    if has_filters:
        sample_ids = biosample_id_search(phenopacket_filters=phenopacket_filters,
                                         experiment_filters=experiment_filters, config_filters=config_filters)
        if not sample_ids:
            return zero_count_response()

    # finally, find relevant variants, depending on whether a variants query was made
    if variants_query:
        # gohan search returns uppercase only
        sample_ids = [id.upper() for id in sample_ids]

        variant_results = query_gohan(variants_query, "record", ids_only=False)
        if has_filters:
            variant_results = list(filter(lambda v: v.get("sample_id") in sample_ids, variant_results))
        gohan_count = len(variant_results)
    else:
        # gohan overview returns lowercase only
        sample_ids = [id.lower() for id in sample_ids]

        variant_totals = gohan_totals_by_sample_id()
        if has_filters:
            gohan_count = sum(variant_totals.get(id) for id in sample_ids if id in variant_totals)
        else:
            gohan_count = sum(variant_totals.values())

    return build_query_response(numTotalResults=gohan_count, full_record_handler=variants_full_results)


def variants_full_results(ids):
    # TODO? eventually
    # requires mapping to beacon format and good pagination
    raise NotImplemented("full response for variants not available")


# -------------------------------------------------------
#       endpoints in beacon model not yet implemented:
#
#       /g_variants/<id>
#       /g_variants/<id>/biosamples
#       /g_variants/<id>/individuals
#
#       ... "id" here appears to be a unique id for each entry, not a variant identifier like a dbSNP entry
# -------------------------------------------------------
