from flask import current_app
from functools import reduce
from .gohan_utils import query_gohan
from .katsu_utils import (
    katsu_filters_query,
    search_from_config,
    biosample_ids_for_individuals,
    individual_ids_for_biosamples,
)
from .beacon_response import add_info_to_response
from .filters import bento_format_filters


# TODO: search by linked field set elements instead of hardcoding
async def biosample_id_search(
    variants_query=None,
    phenopacket_filters=None,
    experiment_filters=None,
    config_filters=None,
    project_id=None,
    dataset_id=None,
):
    results_biosample_ids = {}

    if not (variants_query or phenopacket_filters or experiment_filters or config_filters):
        return []

    if variants_query:
        if not current_app.config["BEACON_CONFIG"].get("useGohan"):
            # variants query even though there are no variants in this beacon, this can happen in a network context
            add_info_to_response("No variants available at this beacon, query by metadata values only")
            return []
        variant_sample_ids = await query_gohan(variants_query, "count", ids_only=True)
        if not variant_sample_ids:
            return []
        results_biosample_ids["variant_sample_ids"] = variant_sample_ids

    if experiment_filters:
        experiment_sample_ids = await katsu_filters_query(
            experiment_filters, "experiment", get_biosample_ids=True, project_id=project_id, dataset_id=dataset_id
        )
        if not experiment_sample_ids:
            return []
        results_biosample_ids["experiment_sample_ids"] = experiment_sample_ids

    # next two return *all* biosample ids for matching individuals

    if phenopacket_filters:
        phenopacket_sample_ids = await katsu_filters_query(
            phenopacket_filters, "phenopacket", get_biosample_ids=True, project_id=project_id, dataset_id=dataset_id
        )
        if not phenopacket_sample_ids:
            return []
        results_biosample_ids["phenopacket_sample_ids"] = phenopacket_sample_ids

    if config_filters:
        config_individuals = await search_from_config(config_filters, project_id=project_id, dataset_id=dataset_id)
        if not config_individuals:
            return []
        results_biosample_ids["config_sample_ids"] = await biosample_ids_for_individuals(config_individuals)

    return list(reduce(set.intersection, (set(ids) for ids in results_biosample_ids.values())))


# ####################################################################################
# Temp proof of concept for ga4gh
# See https://github.com/ga4gh-beacon/beacon-v2/pull/266


def is_legacy_format(filters):
    return all(isinstance(f, dict) for f in filters)


async def individuals_search_with_dnf_filters(
    variants_query=None,
    filters=None,
    project_id=None,
    dataset_id=None,
):

    # read filters in Disjunctive Normal Form

    # any nested list is a disjunct (we allow only a single layer of nesting)
    # So [ [{A}, {B}], [{C}] ] is read as (A & B) v C

    # if filters appear as a single list with no nesting,
    # the entire list is assumed to be a single disjunct

    # This code does not handle "mixed" nesting, eg [ {A}, [{B}] ]
    # so acceptable syntax for filters is either:
    # - all top-level elements are lists (single or multiple disjuncts): [ [], [] ]
    # - all top-level elements are objects (single disjunct): [ {}, {} ]

    # in particular the acceptable formats are:

    # 0. empty: [],
    # 1: nested empty: [[]]
    # 2. single nested disjunct: [ [{A}, {B}] ]
    # 3. multiple disjuncts: [ [{A}, {B}], [{C}] ]
    # 4. single disjunct without nesting (legacy format, equivalent to 1 above): [{A}, {B}]

    # temp hack for legacy format
    if is_legacy_format(filters):
        filters = [filters]

    variants_individual_ids = set()
    filters_individual_ids = set()

    # search gohan once
    if variants_query:
        variant_biosample_ids = await biosample_id_search(variants_query=variants_query)
        # if nothing do early return
        if not variant_biosample_ids:
            return []

        variants_individual_ids.update((await individual_ids_for_biosamples(variant_biosample_ids)))

    # then loop over disjunctive clauses
    for disjunctive_clause in filters:

        # partition into experiment, phenopacket and config filters
        # handle config search only for now
        filters_this_clause = bento_format_filters(disjunctive_clause)
        config_filters = filters_this_clause["config_filters"]

        config_individual_ids = await search_from_config(config_filters, project_id=project_id, dataset_id=dataset_id)

        # union with full results
        filters_individual_ids.update(config_individual_ids)

    if not filters_individual_ids:
        return []

    if variants_query:
        results = list(variants_individual_ids & filters_individual_ids)
    else:
        results = list(filters_individual_ids)

    return results
