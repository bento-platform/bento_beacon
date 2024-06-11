from flask import current_app, g
import requests
from urllib.parse import urlsplit, urlunsplit
from json import JSONDecodeError
from .network_config import BEACONS, NETWORK_TIMEOUT
from ..utils.exceptions import APIException, InvalidQuery
from ..utils.beacon_response import beacon_count_response

DEFAULT_ENDPOINT = "individuals"
OVERVIEW_STATS_QUERY = {
    "meta": {"apiVersion": "2.0.0"},
    "query": {"requestParameters": {}, "filters": [], "includeResultsetResponses": "ALL"},
    "bento": {"showSummaryStatistics": True},
}


def network_beacon_call(method, url, payload=None):
    try:
        if method == "GET":
            r = requests.get(url, timeout=NETWORK_TIMEOUT)
        else:
            r = requests.post(url, json=payload, timeout=NETWORK_TIMEOUT)
        beacon_response = r.json()

    except (requests.exceptions.RequestException, JSONDecodeError) as e:
        current_app.logger.error(e)
        msg = f"beacon network error calling url {url}: {e}"
        raise APIException(message=msg)

    return beacon_response


def network_beacon_get(root_url, endpoint=None):
    url = root_url if endpoint is None else root_url + "/" + endpoint
    return network_beacon_call("GET", url)


def network_beacon_post(root_url, payload={}, endpoint=None):
    url = root_url if endpoint is None else root_url + "/" + endpoint
    return network_beacon_call("POST", url, payload)


def init_network_service_registry():
    current_app.logger.info("registering beacons")
    network_beacons = {}
    failed_beacons = []
    for url in BEACONS:
        try:
            b = network_beacon_get(url, endpoint="overview")
            beacon_info = b.get("response")

        except APIException:
            failed_beacons.append(url)
            current_app.logger.error(f"error contacting network beacon {url}")
            continue

        if not beacon_info:
            failed_beacons.append(url)
            current_app.logger.error(f"bad response from network beacon {url}")
            continue

        beacon_info["apiUrl"] = url

        # organize overview stats
        # TODO (Redmine #2170) modify beacon /overview so we don't have to make two calls here, with different response formats

        # TODO: filters here??
        biosample_and_experiment_stats = (
            network_beacon_post(url, OVERVIEW_STATS_QUERY, DEFAULT_ENDPOINT).get("info", {}).get("bento")
        )
        individual_and_variant_stats = beacon_info.get("overview", {}).get("counts")

        overview = {
            "individuals": {"count": individual_and_variant_stats.get("individuals")},
            "variants": individual_and_variant_stats.get("variants"),
            **biosample_and_experiment_stats,
        }

        b_id = beacon_info.get("id")
        network_beacons[b_id] = beacon_info
        network_beacons[b_id]["overview"] = overview

        # TODO, katsu calls are inconsistent here
        # qs = get_public_search_fields(url)
        # network_beacons[b_id]["querySections"] = get_public_search_fields(url)  # temp

        # make a merged overview?
        # what about merged filtering_terms?
    current_app.logger.info(
        f"registered {len(network_beacons)} beacon{'' if len(network_beacons) == 1 else 's'} in network: {', '.join(network_beacons)}"
    )
    if failed_beacons:
        current_app.logger.error(
            f"{len(failed_beacons)} network beacon{'' if len(failed_beacons) == 1 else 's'} failed to respond: {', '.join(failed_beacons)}"
        )

    current_app.config["NETWORK_BEACONS"] = network_beacons


def beacon_network_response(beacon_responses):
    num_total_results, bento_stats = sum_network_responses(beacon_responses)
    g.response_info["bento"] = bento_stats
    g.response_info["network"] = beacon_responses

    # beacon network hardcoded to counts
    # to handle all possible granularities, call build_query_response() instead
    return beacon_count_response(num_total_results)


def sum_network_responses(beacon_responses):
    num_total_results = 0
    # could parameterize response, currently hardcoded in bento_public
    experiments_count = 0
    biosamples_count = 0
    sampled_tissue_chart = []
    experiment_type_chart = []

    for response in beacon_responses.values():
        num_total_results += response.get("responseSummary", {}).get("numTotalResults", 0)
        stats = response.get("info", {}).get("bento", {})
        experiments_count += stats.get("experiments", {}).get("count")
        biosamples_count += stats.get("biosamples", {}).get("count")
        sampled_tissue_chart = merge_charts(sampled_tissue_chart, stats.get("biosamples", {}).get("sampled_tissue", []))
        experiment_type_chart = merge_charts(
            experiment_type_chart, stats.get("experiments", {}).get("experiment_type", [])
        )

    bento_stats = {
        "biosamples": {"count": biosamples_count, "sampled_tissue": sampled_tissue_chart},
        "experiments": {"count": experiments_count, "experiment_type": experiment_type_chart},
    }

    return num_total_results, bento_stats


def chart_to_dict(chart):
    return {item["label"]: item["value"] for item in chart}


def dict_to_chart(d):
    return [{"label": label, "value": value} for label, value in d.items()]


def merge_charts(c1, c2):
    """
    combine data from two categorical charts
    any categories with identical names are merged into a single field with the sum of their values
    """
    merged = chart_to_dict(c1)
    for cat in c2:
        label = cat["label"]
        value = cat["value"]
        merged[label] = merged.get(label, 0) + value

    return dict_to_chart(merged)


def get_public_search_fields(beacon_url):
    fields_url = public_search_fields_url(beacon_url)
    fields = network_beacon_get(fields_url)
    return fields


def public_search_fields_url(beacon_url):
    split_url = urlsplit(beacon_url)
    return urlunsplit(
        (split_url.scheme, "portal." + split_url.netloc, "/api/metadata/api/public_search_fields", "", "")
    )


def filtersUnion():
    pass


def filtersIntersection():
    pass
