import aiohttp
import asyncio
from flask import current_app
from urllib.parse import urlsplit, urlunsplit
from json import JSONDecodeError
from ..config_files.config import reverse_domain_id
from ..utils.http import tcp_connector
from ..utils.exceptions import APIException
from ..utils.katsu_utils import overview_statistics, get_katsu_config_search_fields
from ..endpoints.info import build_service_details, overview
from ..endpoints.biosamples import get_biosamples
from ..endpoints.cohorts import get_cohorts
from ..endpoints.datasets import get_datasets
from ..endpoints.individuals import get_individuals
from ..endpoints.variants import get_variants
from .bento_public_query import fields_intersection, fields_union

# future versions will pull metadata query info directly from network beacons instead of network katsus
# to deprecate in Bento 18
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
async def info_for_host_beacon():
    service_details = await build_service_details()

    # TODO: fix ugly overlapping overview functions
    # requires rolling out changes to all beacons first
    bento_overview = await overview()
    bento_private_overview = await overview_statistics()
    experiment_stats = {"count": bento_private_overview.get("count", 0)}
    biosample_stats = {
        "count": bento_private_overview.get("phenopacket", {})
        .get("data_type_specific", {})
        .get("biosamples", {})
        .get("count", 0)
    }

    api_url = current_app.config["BEACON_BASE_URL"]

    return {
        **service_details,
        "apiUrl": api_url,
        "overview": {
            "individuals": {"count": bento_overview.get("counts", {}).get("individuals")},
            "variants": bento_overview.get("counts", {}).get("variants", {}),
            "biosamples": biosample_stats,
            "experiments": experiment_stats,
        },
        "querySections": (await get_katsu_config_search_fields(requires_auth="none")).get("sections", []),
    }


async def host_beacon_response(endpoint):
    # endpoint already known to be valid
    return await HOST_VIEWS_BY_ENDPOINT[endpoint]()


def has_variants_query(payload):
    if not payload:
        return False
    query = payload.get("requestParameters", {}).get("g_variant")
    return bool(query)


async def network_beacon_call(method, url, payload=None):
    c = current_app.config
    current_app.logger.info(f"Calling network url: {url}")
    timeout = (
        c["NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS"]
        if has_variants_query(payload)
        else c["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
    )

    try:
        async with aiohttp.ClientSession(connector=tcp_connector(c)) as s:
            if method == "GET":
                r = await s.get(url, timeout=timeout)
            else:
                r = await s.post(url, timeout=timeout, json=payload)

        beacon_response = await r.json()

    except (aiohttp.ClientError, JSONDecodeError) as e:
        current_app.logger.error(e)
        msg = f"beacon network error calling url {url}: {e}"
        raise APIException(message=msg)

    return beacon_response


async def network_beacon_get(root_url, endpoint=None):
    url = root_url if endpoint is None else root_url + "/" + endpoint
    return await network_beacon_call("GET", url)


async def network_beacon_post(root_url, payload={}, endpoint=None):
    url = root_url if endpoint is None else root_url + "/" + endpoint
    return await network_beacon_call("POST", url, payload)


def make_network_filtering_terms(beacons):
    all_query_sections = [b.get("querySections", {}) for b in beacons.values()]
    current_app.config["ALL_NETWORK_FILTERS"] = filters_union(all_query_sections)
    current_app.config["COMMON_NETWORK_FILTERS"] = filters_intersection(all_query_sections)
    pass


async def call_network_beacon_for_init(url):
    current_app.logger.info(f"call_network_beacon_for_init()")
    beacon_info = {"apiUrl": url}

    try:

        b = (await network_beacon_get(url, endpoint="overview")).get("response")
        beacon_info.update(b)

        # organize overview stats
        # TODO (Redmine #2170) modify beacon /overview response
        # .... so we don't have to make two calls here, with different response formats
        individual_and_variant_stats = b.get("overview", {}).get("counts")
        biosample_and_experiment_stats = (
            (await network_beacon_post(url, OVERVIEW_STATS_QUERY, DEFAULT_ENDPOINT)).get("info", {}).get("bento")
        )

        beacon_info["overview"] = {
            "individuals": {"count": individual_and_variant_stats.get("individuals")},
            "variants": individual_and_variant_stats.get("variants"),
            **biosample_and_experiment_stats,
        }

        # temp, call katsu for bento public "query_sections"
        # TODO change to beacon spec filters, don't call katsu
        beacon_info["querySections"] = (await get_public_search_fields(url)).get("sections", [])
        beacon_info["isUp"] = True

    except APIException:
        beacon_info["isUp"] = False
        # assign an id to failed beacons, so client can attempt a call later
        if "id" not in beacon_info:
            beacon_info["id"] = reverse_domain_id(url.removeprefix("https://").removesuffix("/api/beacon"))

    return beacon_info


async def init_network_service_registry():
    current_app.logger.info("registering beacons")
    urls = current_app.config["NETWORK_URLS"]
    if not urls:
        current_app.logger.error("can't find urls for beacon network, did you forget a config file?")
        raise APIException("can't find urls for beacon network")

    host_beacon_url = current_app.config["BEACON_BASE_URL"]
    current_app.logger.debug(f"host url: {host_beacon_url}")

    calls = []
    for url in urls:

        # special handling for calling the beacon this network is hosted on
        if url == host_beacon_url:
            calls.append(info_for_host_beacon())
            continue

        # all other beacons
        calls.append(call_network_beacon_for_init(url))

    current_app.logger.info(f"calling {len(urls)} beacons in network")
    results = await asyncio.gather(*calls, return_exceptions=True)

    # # make a merged overview?
    # # what about merged filtering_terms?
    current_app.logger.info(f"registered {len(results)} beacon{'' if len(results) == 1 else 's'} in network")

    # dict by beacon id easier to work with elsewhere
    beacon_dict = {b["id"]: b for b in results}

    make_network_filtering_terms(beacon_dict)
    # current_app.config["NETWORK_BEACONS"] = network_beacons

    return beacon_dict


##########################################
# Temp utils for bento public search terms


# deprecate in Bento 18
async def get_public_search_fields(beacon_url):
    fields_url = public_search_fields_url(beacon_url)
    current_app.logger.info(f"trying public fields url {fields_url}")
    fields = await network_beacon_get(fields_url)
    return fields


# deprecate in Bento 18
def public_search_fields_url(beacon_url):
    split_url = urlsplit(beacon_url)
    return urlunsplit((split_url.scheme, "portal." + split_url.netloc, PUBLIC_SEARCH_FIELDS_PATH, "", ""))


def filters_union(all_search_fields):
    return [{"section_title": "All Filters", "fields": fields_union(all_search_fields)}]


def filters_intersection(all_search_fields):
    return [{"section_title": "Common Filters", "fields": fields_intersection(all_search_fields)}]
