from flask import current_app
from functools import reduce
from .gohan_utils import query_gohan
from .katsu_utils import katsu_filters_query, search_from_config, biosample_ids_for_individuals
from .beacon_response import add_info_to_response


# TODO: search by linked field set elements instead of hardcoding
def biosample_id_search(variants_query=None, phenopacket_filters=None, experiment_filters=None, config_filters=None):
    results_biosample_ids = {}

    if not (variants_query or phenopacket_filters or experiment_filters or config_filters):
        return []

    if variants_query:
        if not current_app.config["BEACON_CONFIG"].get("useGohan"):
            # variants query even though there are no variants in this beacon, this can happen in a network context
            add_info_to_response("No variants available at this beacon, query by metadata values only")
            return []
        variant_sample_ids = query_gohan(variants_query, "count", ids_only=True)
        if not variant_sample_ids:
            return []
        results_biosample_ids["variant_sample_ids"] = variant_sample_ids

    if experiment_filters:
        experiment_sample_ids = katsu_filters_query(experiment_filters, "experiment", get_biosample_ids=True)
        if not experiment_sample_ids:
            return []
        results_biosample_ids["experiment_sample_ids"] = experiment_sample_ids

    # next two return *all* biosample ids for matching individuals

    if phenopacket_filters:
        phenopacket_sample_ids = katsu_filters_query(phenopacket_filters, "phenopacket", get_biosample_ids=True)
        if not phenopacket_sample_ids:
            return []
        results_biosample_ids["phenopacket_sample_ids"] = phenopacket_sample_ids

    if config_filters:
        config_individuals = search_from_config(config_filters)
        if not config_individuals:
            return []
        results_biosample_ids["config_sample_ids"] = biosample_ids_for_individuals(config_individuals)

    return list(reduce(set.intersection, (set(ids) for ids in results_biosample_ids.values())))
