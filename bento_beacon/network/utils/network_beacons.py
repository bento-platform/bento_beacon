import asyncio
import aiohttp
from json import JSONDecodeError
from abc import ABC, abstractmethod
from flask import current_app
from .filters import get_filters_dict, get_intersection_of_filtering_terms, get_union_of_filtering_terms, flatten
from ...utils.http import tcp_connector
from ...utils.exceptions import APIException
from ...utils.censorship import set_censorship
from ...endpoints.biosamples import get_biosamples
from ...endpoints.cohorts import get_cohorts
from ...endpoints.datasets import get_datasets
from ...endpoints.individuals import get_individuals
from ...endpoints.variants import get_variants
from ...endpoints.info import beacon_format_service_details as local_beacon_format_service_details
from ...endpoints.info_scoped import (
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


# parent class for host beacon & beacons in the network
class NetworkNode(ABC):

    # shared constructor for subclasses
    def __init__(self, node_config, app_config, logger):
        self.api_url = node_config.get("api_url")
        self.node_config = node_config  # network config for this node
        self.app_config = app_config  # flask config
        self.logger = logger

        # filled in after calls
        self.id = None
        self.bento_beacon_version = None
        self.service_details = None
        self.overview = None
        self.filtering_terms = None

    @abstractmethod
    async def retrieve_beacon_info(self):
        pass

    @abstractmethod
    async def query_beacon(self, payload, endpoint):
        pass

    def node_info_to_json(self):
        # filtering terms?
        return {**self.service_details, "apiUrl": self.api_url, "overview": self.overview}


class HostBeacon(NetworkNode):

    async def retrieve_beacon_info(self):
        self.service_details = await local_beacon_format_service_details()
        self.id = self.service_details.get("id")
        self.bento_beacon_version = self.service_details.get("version")
        self.overview = await local_beacon_overview()
        self.filtering_terms = await local_beacon_filtering_terms(project_id=None, dataset_id=None)

    async def query_beacon(self, _, endpoint):
        # apply censorship for local beacon
        # other nodes in network handle their own censorship settings
        await set_censorship()

        # payload is pulled directly from request data rather than passed here
        # endpoint already known to be valid
        return await HOST_VIEWS_BY_ENDPOINT[endpoint]()


class NetworkBeacon(NetworkNode):

    async def retrieve_beacon_info(self):
        # two network calls, but both are to the same beacon
        overview_response = (await self._network_beacon_get(OVERVIEW_ENDPOINT)).get("response")
        service_details = {k: v for k, v in overview_response.items() if k != "overview"}
        overview = overview_response.get("overview", {})
        self.service_details = service_details
        self.id = self.service_details.get("id")
        self.overview = overview

        self.filtering_terms = await self.get_filtering_terms()

    async def get_filtering_terms(self):
        try:
            response = (await self._network_beacon_get(FILTERING_TERMS_ENDPOINT)).get("response", {})
        except APIException:
            self.logger.error(f"failed to retrieve filtering terms from beacon {self.id}")
            response = {}

        filters = response.get("filteringTerms", [])

        # if there are versioning changes necessary for this beacon, apply them here

        return filters

    async def query_beacon(self, payload, endpoint):
        # apply any versioning to request payload

        results = await self._network_beacon_post(payload, endpoint)

        # apply any versioning to response format
        return results

    def request_timeout(self, payload=None):
        return (
            self.app_config["NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS"]
            if self.has_variants_query(payload)
            else self.app_config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        )

    def has_variants_query(self, payload):
        if not payload:
            return False
        query = payload.get("requestParameters", {}).get("g_variant")
        return bool(query)

    async def _network_beacon_call(self, method, url, payload=None):
        self.logger.info(f"Calling network url: {url}")
        timeout = self.request_timeout(payload)

        try:
            async with aiohttp.ClientSession(connector=tcp_connector(self.app_config)) as s:
                async with (
                    s.get(url, timeout=timeout) if method == "GET" else s.post(url, timeout=timeout, json=payload)
                ) as r:
                    if not r.ok:
                        self.logger.error(f"failed network call to {url}")
                        raise APIException()
                    beacon_response = await r.json()

        except (APIException, aiohttp.ClientError, JSONDecodeError) as e:
            msg = f"beacon network error calling url {url}: {e}"
            raise APIException(message=msg)

        return beacon_response

    async def _network_beacon_get(self, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        return await self._network_beacon_call("GET", url)

    async def _network_beacon_post(self, payload, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        return await self._network_beacon_call("POST", url, payload)


# -----------------------------------


async def init_network_service_registry(network_config, app_config, logger):
    network_beacons = network_config.get("beacons")
    host_beacon_url = app_config["BEACON_BASE_URL"]

    # instantiate skeleton beacon objects
    beacons = []
    for node_config in network_beacons.values():
        if node_config.get("api_url") == host_beacon_url:
            beacons.append(HostBeacon(node_config, app_config, logger))
        else:
            beacons.append(NetworkBeacon(node_config, app_config, logger))

    # fill in service details and filtering terms for each beacon
    beacon_calls = [b.retrieve_beacon_info() for b in beacons]
    await asyncio.gather(*beacon_calls, return_exceptions=True)

    # filter out failed beacons
    # could add extra handling for failed beacons in the future
    responding_beacons = [b for b in beacons if b.id is not None]

    # create network-wide filtering terms
    network_filtering_terms = await get_network_filtering_terms(responding_beacons)

    # save beacons as a dict by id
    current_app.config["NETWORK_BEACONS"] = {b.id: b for b in responding_beacons}

    results = {
        "beacons": [b.node_info_to_json() for b in responding_beacons],
        "filtersIntersection": network_filtering_terms.get("filtersIntersection"),
        "filtersUnion": network_filtering_terms.get("filtersUnion"),
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
