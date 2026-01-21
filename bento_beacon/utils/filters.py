# replace compact phenopacket and experiment ids with native bento format
def expand_path(id):
    return id.replace("/", ".[item].")


def bento_format_filters(request_filters):
    phenopacket_filters = [f for f in request_filters if f["id"].startswith("phenopacket.")]
    experiment_filters = [f for f in request_filters if f["id"].startswith("experiment.")]
    config_filters = [f for f in request_filters if f not in phenopacket_filters and f not in experiment_filters]

    phenopacket_filters_bento = [
        {"id": expand_path(f["id"]).removeprefix("phenopacket."), "operator": f["operator"], "value": f["value"]}
        for f in phenopacket_filters
    ]
    experiment_filters_bento = [
        {"id": expand_path(f["id"]).removeprefix("experiment."), "operator": f["operator"], "value": f["value"]}
        for f in experiment_filters
    ]

    return {
        "phenopacket_filters": phenopacket_filters_bento,
        "experiment_filters": experiment_filters_bento,
        "config_filters": config_filters,
    }
