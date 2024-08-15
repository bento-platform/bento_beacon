import requests
from flask import current_app
from urllib.parse import urlsplit, urlunsplit
from json import JSONDecodeError
from ..utils.exceptions import APIException
from ..utils.katsu_utils import overview_statistics, get_katsu_config_search_fields
from ..endpoints.info import build_service_details, overview
from ..endpoints.biosamples import get_biosamples
from ..endpoints.cohorts import get_cohorts
from ..endpoints.datasets import get_datasets
from ..endpoints.individuals import get_individuals
from ..endpoints.variants import get_variants
from .bento_public_query import fields_intersection, fields_union

PUBLIC_SEARCH_FIELDS_PATH = "/api/metadata/api/public_search_fields"
DEFAULT_ENDPOINT = "individuals"
OVERVIEW_STATS_QUERY = {
    "meta": {"apiVersion": "2.0.0"},
    "query": {"requestParameters": {}, "filters": [], "includeResultsetResponses": "ALL"},
    "bento": {"showSummaryStatistics": True},
}
HOST_VIEWS_BY_ENDPOINT = {
    "biosamples": get_biosamples,
    "cohorts": get_cohorts,
    "datasets": get_datasets,
    "individuals": get_individuals,
    "variants": get_variants,
}


# get network node info for this beacon, which is also hosting the network
# call methods directly instead of circular http calls
def info_for_host_beacon():
    service_details = build_service_details()

    # TODO: fix ugly overlapping overview functions
    # requires rolling out changes to all beacons first
    bento_overview = overview()
    biosample_and_experiment_stats = overview_statistics()
    api_url = current_app.config["BEACON_BASE_URL"]

    return {
        **service_details,
        "apiUrl": api_url,
        "b_id": current_app.config["BEACON_ID"],
        "overview": {
            "individuals": {"count": bento_overview.get("counts", {}).get("individuals")},
            "variants": bento_overview.get("variants", {}),
            **biosample_and_experiment_stats,
        },
        "querySections": get_katsu_config_search_fields().get("sections", []),
    }


def host_beacon_response(endpoint):
    # endpoint already known to be valid
    return HOST_VIEWS_BY_ENDPOINT[endpoint]()


def has_variants_query(payload):
    if not payload:
        return False
    query = payload.get("requestParameters", {}).get("g_variant")
    return bool(query)


# TODO: timeout param
def network_beacon_call(method, url, payload=None):
    current_app.logger.info(f"Calling network url: {url}")
    timeout = (
        current_app.config["NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS"]
        if has_variants_query(payload)
        else current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
    )

    try:
        if method == "GET":
            r = requests.get(url, timeout=timeout)
        else:
            r = requests.post(url, json=payload, timeout=timeout)
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


def make_network_filtering_terms(beacons):
    all_query_sections = [b["querySections"] for b in beacons.values()]
    current_app.config["ALL_NETWORK_FILTERS"] = filters_union(all_query_sections)
    current_app.config["COMMON_NETWORK_FILTERS"] = filters_intersection(all_query_sections)
    pass


def init_network_service_registry():
    current_app.logger.info("registering beacons")
    urls = current_app.config["NETWORK_URLS"]
    network_beacons = {}
    failed_beacons = []
    host_beacon_url = current_app.config["BEACON_BASE_URL"]
    current_app.logger.debug(f"host url: {host_beacon_url}")
    for url in urls:

        # special handling for calling the beacon this network is hosted on
        if url == host_beacon_url:
            host_id = current_app.config["BEACON_ID"]
            network_beacons[host_id] = info_for_host_beacon()
            continue

        # all other beacons
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

        # Note: v15 katsu does not respond here
        # TODO (longer): serve beacon spec filtering terms instead of bento public querySections
        network_beacons[b_id]["querySections"] = get_public_search_fields(url).get("sections", [])  # temp

        # make a merged overview?
        # what about merged filtering_terms?
    current_app.logger.info(
        f"registered {len(network_beacons)} beacon{'' if len(network_beacons) == 1 else 's'} in network: {', '.join(network_beacons)}"
    )
    if failed_beacons:
        current_app.logger.error(
            f"{len(failed_beacons)} network beacon{'' if len(failed_beacons) == 1 else 's'} failed to respond: {', '.join(failed_beacons)}"
        )

    make_network_filtering_terms(network_beacons)
    current_app.config["NETWORK_BEACONS"] = network_beacons


##########################################
# Temp utils for bento public search terms


def get_public_search_fields(beacon_url):
    fields_url = public_search_fields_url(beacon_url)
    current_app.logger.info(f"trying public fields url {fields_url}")
    fields = network_beacon_get(fields_url)
    return fields


def public_search_fields_url(beacon_url):
    split_url = urlsplit(beacon_url)
    return urlunsplit((split_url.scheme, "portal." + split_url.netloc, PUBLIC_SEARCH_FIELDS_PATH, "", ""))


def filters_union(all_search_fields):
    return [{"section_title": "All Filters", "fields": fields_union(all_search_fields)}]


def filters_intersection(all_search_fields):
    return [{"section_title": "Common Filters", "fields": fields_intersection(all_search_fields)}]
