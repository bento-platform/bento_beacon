import aiohttp
import asyncio
from flask import current_app
from packaging.version import Version
from urllib.parse import urlsplit, urlunsplit
from json import JSONDecodeError
from ..utils.http import tcp_connector
from ..utils.exceptions import APIException
from ..utils.katsu_utils import get_katsu_config_search_fields
from ..utils.censorship import set_censorship
from ..endpoints.info import beacon_format_service_details
from ..endpoints.info_scoped import overview
from ..endpoints.biosamples import get_biosamples
from ..endpoints.cohorts import get_cohorts
from ..endpoints.datasets import get_datasets
from ..endpoints.individuals import get_individuals
from ..endpoints.variants import get_variants
from .bento_public_query import fields_intersection, fields_union

# future versions will pull metadata query info directly from network beacons instead of network katsus
# to deprecate in Bento 19
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

# temp hack to accommodate katsu url changes in Bento 18 (== beacon 0.19.0)
# we should not call katsu at all in later versions
BEACON_VERSION_ZERO_POINT_NINETEEN = Version("0.19.0")


# get network node info for this beacon, which is also hosting the network
# call methods directly instead of circular http calls
async def info_for_host_beacon():
    service_details = await beacon_format_service_details()
    bento_overview = await overview()
    api_url = current_app.config["BEACON_BASE_URL"]

    return {
        **service_details,
        "apiUrl": api_url,
        "overview": bento_overview,
        "querySections": (await get_katsu_config_search_fields()).get("sections", []),
    }


async def host_beacon_response(endpoint):
    # we're bypassing the usual route to host beacon, so have to invoke censorship manually
    await set_censorship()

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
            async with (
                s.get(url, timeout=timeout) if method == "GET" else s.post(url, timeout=timeout, json=payload)
            ) as r:

                if not r.ok:
                    raise APIException()

                beacon_response = await r.json()

    except (APIException, aiohttp.ClientError, JSONDecodeError) as e:
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
        beacon_info["querySections"] = (await get_public_search_fields(beacon_info)).get("sections", [])

    except APIException as e:
        current_app.logger.error(f"failed trying to initialize network beacon {url}")
        raise e

    return beacon_info


async def init_network_service_registry():
    urls = current_app.config["NETWORK_URLS"]
    if not urls:
        current_app.logger.error("can't find urls for beacon network, did you forget a config file?")
        raise APIException("can't find urls for beacon network")

    current_app.logger.info(f"registering {len(urls)} beacons")

    host_beacon_url = current_app.config["BEACON_BASE_URL"]

    calls = []
    for url in urls:

        # special handling for calling the beacon this network is hosted on
        if url == host_beacon_url:
            calls.append(info_for_host_beacon())
            continue

        # all other beacons
        calls.append(call_network_beacon_for_init(url))

    results = await asyncio.gather(*calls, return_exceptions=True)

    # filter out any failed calls
    registered_beacons = [b for b in results if not isinstance(b, Exception)]

    current_app.logger.info(f"registered {len(registered_beacons)} beacon(s) in network")
    num_failed = len(results) - len(registered_beacons)
    if num_failed:
        current_app.logger.info(f"{num_failed} beacon(s) failed to register")

    # dict by beacon id easier to work with elsewhere
    beacon_dict = {b["id"]: b for b in registered_beacons}

    make_network_filtering_terms(beacon_dict)
    current_app.config["NETWORK_BEACONS"] = beacon_dict

    return beacon_dict


##########################################
# Temp utils for bento public search terms


def is_pr_build(version_string):
    return version_string.startswith("pr-")


def is_below_bento_beacon_version_19(beacon):
    version_string = beacon["version"]
    # pr version names break version parsing but are assumed to be recent
    if is_pr_build(version_string):
        return False
    return Version(version_string) < BEACON_VERSION_ZERO_POINT_NINETEEN


# to deprecate
async def get_public_search_fields(beacon):
    fields_url = public_search_fields_url(beacon)
    current_app.logger.info(f"trying public fields url {fields_url}")
    fields = await network_beacon_get(fields_url)
    return fields


# to deprecate
def public_search_fields_url(beacon):
    # fix for katsu url change in Bento 18
    url_prefix = "portal." if is_below_bento_beacon_version_19(beacon) else ""

    split_url = urlsplit(beacon["apiUrl"])
    return urlunsplit((split_url.scheme, url_prefix + split_url.netloc, PUBLIC_SEARCH_FIELDS_PATH, "", ""))


def filters_union(all_search_fields):
    return [{"section_title": "All Filters", "fields": fields_union(all_search_fields)}]


def filters_intersection(all_search_fields):
    return [{"section_title": "Common Filters", "fields": fields_intersection(all_search_fields)}]
