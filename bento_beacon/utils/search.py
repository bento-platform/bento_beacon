from functools import reduce
from .gohan_utils import query_gohan
from .katsu_utils import katsu_filters_query, search_from_config


# TODO: search by linked field set elements instead of hardcoding
def biosample_id_search(variants_query=None, phenopacket_filters=None, experiment_filters=None, config_filters=None):
    results_biosample_ids = {}

    if not (variants_query or phenopacket_filters or experiment_filters or config_filters):
        return []

    if variants_query:
        variant_sample_ids = query_gohan(variants_query, "count", ids_only=True)
        if not variant_sample_ids:
            return []
        results_biosample_ids["variant_sample_ids"] = variant_sample_ids

    if experiment_filters:
        experiment_sample_ids = katsu_filters_query(experiment_filters, "experiment", get_biosample_ids=True)
        if not experiment_sample_ids:
            return []
        results_biosample_ids["experiment_sample_ids"] = experiment_sample_ids

    if phenopacket_filters:
        phenopacket_sample_ids = katsu_filters_query(phenopacket_filters, "phenopacket", get_biosample_ids=True)
        if not phenopacket_sample_ids:
            return []
        results_biosample_ids["phenopacket_sample_ids"] = phenopacket_sample_ids

    if config_filters:
        config_biosample_ids = search_from_config(config_filters)
        if not config_biosample_ids:
            return []
        results_biosample_ids["config_biosample_ids"] = config_biosample_ids
    
    return list(reduce(set.intersection, (set(ids) for ids in results_biosample_ids.values())))
