from flask import Blueprint
from ..authz.middleware import authz_middleware
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response, add_info_to_response
from ..utils.gohan_utils import query_gohan, gohan_total_variants_count, gohan_totals_by_sample_id
from ..utils.katsu_utils import katsu_filters_query
from ..utils.exceptions import NotImplemented

variants = Blueprint("variants", __name__)

# returns counts only
@variants.route("/g_variants", methods=['GET', 'POST'])
@authz_middleware.deco_public_endpoint  # TODO: for now. eventually, return more depending on permissions
def get_variants():
    variants_query, phenopacket_filters, experiment_filters = query_parameters_from_request()

    # if no query, return total count of variants
    if not (variants_query or phenopacket_filters or experiment_filters):
        add_info_to_response("no query found, returning total count")
        total_count = gohan_total_variants_count()
        return beacon_response({"count": total_count})

    if phenopacket_filters:
        phenopacket_sample_ids = katsu_filters_query(phenopacket_filters, "phenopacket", get_biosample_ids=True)
        if not phenopacket_sample_ids:
            return beacon_response({"count": 0, "results": []})

    if experiment_filters:
        experiment_sample_ids = katsu_filters_query(experiment_filters, "experiment", get_biosample_ids=True)
        if not experiment_sample_ids:
            return beacon_response({"count": 0, "results": []})

    # compute cases for results
    # some redundant bools for clarity
    sample_ids = []
    if phenopacket_filters and experiment_filters:
        sample_ids = list(set(phenopacket_sample_ids) & set(experiment_sample_ids))
        # another early return if empty?
    if phenopacket_filters and not experiment_filters:
        sample_ids = phenopacket_sample_ids
    if experiment_filters and not phenopacket_filters:
        sample_ids = experiment_sample_ids

    # workaround for casing issues in gohan
    sample_ids = [id.upper() for id in sample_ids]

    # finally, find relevant variants, depending on whether a variants query was made
    if variants_query:
        variant_results = query_gohan(variants_query, "record", ids_only=False)
        if phenopacket_filters or experiment_filters:
            variant_results = list(filter(lambda v: v.get("sample_id") in sample_ids, variant_results))
        gohan_count = len(variant_results)
    else:
        variant_totals = gohan_totals_by_sample_id()
        if phenopacket_filters or experiment_filters:
            gohan_count = sum(variant_totals.get(id) for id in sample_ids)
        else:
            gohan_count = sum(variant_totals.values())

    return beacon_response({"count": gohan_count})


# -------------------------------------------------------
#       "by id" endpoints
# -------------------------------------------------------
#
# These aren't useful for a counts-only beacon (you will never know any ids)

@variants.route("/g_variants/<id>", methods=['GET', 'POST'])
def variant_by_id(id):  # TODO: authz
    # get one variant by (internal) id
    raise NotImplemented()


@variants.route("/g_variants/<id>/biosamples", methods=['GET', 'POST'])
def biosamples_by_variant(id):  # TODO: authz
    # all biosamples for a particular variant
    raise NotImplemented()


@variants.route("/g_variants/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_variant(id):  # TODO: authz
    # all individuals for a particular variant
    raise NotImplemented()
