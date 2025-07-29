import asyncio
import aiohttp
from json import JSONDecodeError
from abc import ABC, abstractmethod
from copy import deepcopy
from flask import current_app
from ..utils.http import tcp_connector
from ..utils.exceptions import APIException
from ..endpoints.biosamples import get_biosamples
from ..endpoints.cohorts import get_cohorts
from ..endpoints.datasets import get_datasets
from ..endpoints.individuals import get_individuals
from ..endpoints.variants import get_variants
from ..endpoints.info import beacon_format_service_details as local_beacon_format_service_details
from ..endpoints.info_scoped import (
    get_filtering_terms as local_beacon_filtering_terms,
    overview as local_beacon_overview,
)

OVERVIEW_ENDPOINT = "overview"
FILTERING_TERMS_ENDPOINT = "filtering_terms"

HOST_VIEWS_BY_ENDPOINT = {
    "biosamples": get_biosamples,
    "cohorts": get_cohorts,
    "datasets": get_datasets,
    "individuals": get_individuals,
    "variants": get_variants,
}


class NetworkNode(ABC):

    # shared constructor for subclasses
    def __init__(self, config):
        current_app.logger.info(f"init beacon {config.get('name')}")
        self.config = config  # needed? we can just pull what we need / partition into useful parts
        self.api_url = config.get("api_url")
        self.id = config.get("id")

        # filled in later
        self.service_details = None
        self.overview = None
        self.filtering_terms = None

        # self.bento_beacon_version = service_details.get("version")

    @abstractmethod
    async def retrieve_beacon_info(self):
        pass

    @abstractmethod
    async def query_beacon(self):
        pass

    def node_info_to_json(self):
        # filtering terms?
        return {**self.service_details, "apiUrl": self.api_url}


class HostBeacon(NetworkNode):

    async def retrieve_beacon_info(self):
        # gather? most of this code isn't really async
        self.service_details = await local_beacon_format_service_details()
        self.overview = (await local_beacon_overview()).get("overview", {})
        self.filtering_terms = await local_beacon_filtering_terms(project_id=None, dataset_id=None)

    async def query_beacon(self):
        return {}


class NetworkBeacon(NetworkNode):

    async def retrieve_beacon_info(self):
        # two network calls, but both are to the same beacon
        overview_response = (await self._network_beacon_get(OVERVIEW_ENDPOINT)).get("response")
        service_details = {k: v for k, v in overview_response.items() if k != "overview"}
        overview = overview_response.get("overview", {})
        # does not handle API error
        filtering_terms = (
            (await self._network_beacon_get(FILTERING_TERMS_ENDPOINT)).get("response", {}).get("filteringTerms", [])
        )

        # if there are versioning changes necessary for this beacon, apply them here (or on the fly?)
        # then save
        self.service_details = service_details
        self.overview = overview
        self.filtering_terms = filtering_terms

    async def query_beacon(self, payload, endpoint):
        # apply any versioning to request payload
        results = await self._network_beacon_post(payload, endpoint)
        # apply any versioning to response format
        return results

    def request_timeout(self, payload=None):
        return (
            current_app.config["NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS"]
            if self.has_variants_query(payload)
            else current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        )

    async def _network_beacon_call(self, method, url, timeout, payload=None):
        current_app.logger.info(f"Calling network url: {url}")
        try:
            async with aiohttp.ClientSession(connector=tcp_connector(current_app.config)) as s:
                async with (
                    s.get(url, timeout=timeout) if method == "GET" else s.post(url, timeout=timeout, json=payload)
                ) as r:
                    if not r.ok:
                        current_app.logger.error("failed network call to {url}")
                        raise APIException()
                    beacon_response = await r.json()

        except (APIException, aiohttp.ClientError, JSONDecodeError) as e:
            msg = f"beacon network error calling url {url}: {e}"
            raise APIException(message=msg)

        return beacon_response

    async def _network_beacon_get(self, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        timeout = current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        return await self._network_beacon_call("GET", url, timeout)

    async def _network_beacon_post(self, payload, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        timeout = self.request_timeout(payload)
        return await self._network_beacon_call("POST", url, timeout, payload)


# -----------------------------------


async def new_init_network_service_registry():
    config = current_app.config["NEW_NETWORK_CONFIG"]
    network_beacons = config.get("beacons")
    host_beacon_url = current_app.config["BEACON_BASE_URL"]

    # instantiate skeleton beacon objects
    beacons = []
    for beacon_config in network_beacons.values():
        if beacon_config.get("api_url") == host_beacon_url:
            beacons.append(HostBeacon(beacon_config))
        else:
            beacons.append(NetworkBeacon(beacon_config))

    # fill in service details and filtering terms for each beacon
    beacon_calls = []
    for b in beacons:
        beacon_calls.append(b.retrieve_beacon_info())
    await asyncio.gather(*beacon_calls, return_exceptions=False)

    # retrieve_beacon_info() returns None... perhaps could return True on success
    # don't throw away beacons that fail to respond... add handling for these
    # we can try them again later
    # also these errors are logged elsewhere so don't bother logging them here

    # create network-wide filtering terms
    # do we need to save these?
    network_filtering_terms = await get_network_filtering_terms(beacons)

    # collect network assemblies
    # not strictly necessary since client can already get this from response
    # network_reference_assemblies = get_network_reference_assemblies(beacons)

    # save beacons as a dict by id
    # alternatively, make a Network class and save there instead
    current_app.config["NETWORK_BEACONS"] = {b.id: b for b in beacons}

    results = {
        "beacons": [b.node_info_to_json() for b in beacons],
        "filtersIntersection": network_filtering_terms.get("filtersIntersection"),
        "filtersUnion": network_filtering_terms.get("filtersUnion"),
        # "referenceAssemblies": network_reference_assemblies,
    }

    return results


async def get_network_filtering_terms(beacons: list[NetworkNode]):
    all_filtering_terms = [b.filtering_terms for b in beacons if b.filtering_terms is not None]
    num_beacons_answering = len(all_filtering_terms)

    filters_dict = get_filters_dict(flatten(all_filtering_terms))
    return {
        "filtersUnion": get_union_of_filtering_terms(filters_dict),
        "filtersIntersection": get_intersection_of_filtering_terms(filters_dict, num_beacons_answering),
    }


# -------------------------------
# filter utils
# could probably go in a different file


def flatten(nested_list):
    return [item for nested_items in nested_list for item in nested_items]


def get_union_of_filtering_terms(filters_dict):
    # create an entry for each filter
    union_filters = []
    for f in filters_dict.values():
        filter = deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        filter["values"] = values_union([entry["values"] for entry in f])
        union_filters.append(filter)

    return union_filters


def get_intersection_of_filtering_terms(filters_dict, num_beacons_in_network):
    # remove any fields not in all entries
    intersection_dict = {id: entries for id, entries in filters_dict.items() if len(entries) == num_beacons_in_network}

    # create one entry for each id
    intersection_filters = []
    for f in intersection_dict.values():
        filter = deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        values = values_intersection([entry["values"] for entry in f])
        if values:
            filter["values"] = values
            intersection_filters.append(filter)

    return intersection_filters


def get_filters_dict(filters_list):
    # make a dict of entries, keyed to bento query id, keeping duplicates in an array
    # TODO: change key to model mapping (phenopackets / experiments path) instead of bento id
    filters_by_id = {}
    for f in filters_list:
        filter_id = f["id"]
        filters_by_id[filter_id] = filters_by_id.get(filter_id, []) + [f]
    return filters_by_id


def values_union(options_list):
    # remove duplicates but keep any ordering
    return list(dict.fromkeys(flatten(options_list[:])))


def values_intersection(options_list):
    num_instances = len(options_list)
    flat_options = flatten(options_list[:])
    # only keep options that are present in all instances, preserving order
    counter = {}
    for option in flat_options:
        counter[option] = counter.get(option, 0) + 1

    intersection = [key for key in counter if counter[key] == num_instances]
    return intersection


# -----------------------
# reference utils

# TODO later:
# links for gene name lookups for each assembly (some may not exist in local beacon)
# note that for network queries, we only need gene *names*, position information is looked up locally on each beacon.


# needed? can already be inferred by client
def get_network_reference_assemblies(beacons: list[NetworkNode]):
    network_assemblies = set()
    for b in beacons:
        assemblies = list(b.overview.get("variants", {}).keys())
        network_assemblies.update(assemblies)
    return sorted(list(network_assemblies))
