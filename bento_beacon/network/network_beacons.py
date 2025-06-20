import asyncio
import aiohttp
from abc import ABC, abstractmethod
from flask import current_app
from json import JSONDecodeError
from packaging.version import Version
from urllib.parse import urljoin
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
from ..utils.http import tcp_connector

OVERVIEW_ENDPOINT = "/overview"

HOST_VIEWS_BY_ENDPOINT = {
    "biosamples": get_biosamples,
    "cohorts": get_cohorts,
    "datasets": get_datasets,
    "individuals": get_individuals,
    "variants": get_variants,
}


async def new_info_for_host_beacon():
    return {"info for host": "beacon"}


# class for network possibly overkill
# only functionality we need is:
#  - list of beacons / list of filtering terms
#  - query a beacon
#  - we don't even need to query the whole network, since that's done in the UI client


class NetworkBeacon(ABC):

    # shared constructor for subclasses
    def __init__(self, beacon_name, api_url, service_details, overview, filtering_terms):
        current_app.logger.info(f"init beacon {beacon_name}")
        self.beacon_name: str = beacon_name
        self.api_url: str = api_url
        self.service_details: dict = service_details  # "service_details"? not "service_info"?
        self.bento_beacon_version = service_details.get("version")
        # required fields in service details:
        # - id
        # - name
        # - apiVersion
        # - environment
        # - organization (nested obj)

        self.overview: dict = overview
        self.filtering_terms: list = filtering_terms
        # more params

    # factory method for async init
    @classmethod
    @abstractmethod
    async def init_beacon(cls, beacon_name, api_url):
        pass

    @abstractmethod
    async def get_network_beacon_info(self):
        pass

    @abstractmethod
    async def get_overview(self):
        pass

    @abstractmethod
    async def get_filtering_terms(self):
        pass

    @abstractmethod
    async def query_beacon(self):
        pass


# all responses should be **without** the beacon response wrapper, since this is added at the end


class HostNode(NetworkBeacon):
    """
    Class for the local beacon that is also hosting the network.
    Network hosts are not required to have beacons of their own, although this is the typical use case.
    For this local beacon we call python methods directly instead of making circular http calls.
    """

    @classmethod
    async def init_beacon(cls, beacon_name, api_url):
        current_app.logger.info("init host beacon")

        # call python methods instead of circular http calls
        service_details = await local_beacon_format_service_details()
        overview = await local_beacon_overview()  # has response wrapper
        filtering_terms = await local_beacon_filtering_terms(project_id=None, dataset_id=None)
        return cls(beacon_name, api_url, service_details, overview, filtering_terms)

    async def get_network_beacon_info(self):
        # get overview & filtering_terms here, save in obj & return
        # what is this method for? populating values?
        return "host info"

    async def get_overview(self):
        return 0

    async def get_filtering_terms(self):
        return 0

    async def query_beacon(self):
        return 0


class BentoNetworkNode(NetworkBeacon):
    """
    Class for a bento beacon in the network other than the host beacon
    """

    @classmethod
    async def init_beacon(cls, beacon_name, api_url):
        current_app.logger.info(f"init network beacon {beacon_name}")
        timeout = current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        overview_url = api_url + OVERVIEW_ENDPOINT

        service_details_and_overview = (await BentoNetworkNode._network_beacon_call("GET", overview_url, timeout)).get(
            "response", {}
        )
        service_details = {k: v for k, v in service_details_and_overview.items() if k != "overview"}
        overview = service_details_and_overview.get("response", {}).get("overview", {})

        filtering_terms = (
            (await BentoNetworkNode._network_beacon_call("GET", overview_url, timeout))
            .get("response", {})
            .get("filteringTerms", [])
        )

        return cls(beacon_name, api_url, service_details, overview, filtering_terms)

    # needs versioning
    async def get_overview(self):
        overview = await self._network_beacon_get("/overview").get("response")
        return overview

    # needs versioning
    async def get_filtering_terms(self):
        filters = await self._network_beacon_get("/filtering_terms").get("response")
        return 0

    # needs versioning
    async def query_beacon(self, payload, endpoint):
        return await self._network_beacon_post(payload, endpoint)

    # class method since we need to make api calls before calling the constructor
    @classmethod
    async def _network_beacon_call(cls, method, url, timeout, payload=None):

        current_app.logger.info(f"Calling network url: {url}")

        try:
            async with aiohttp.ClientSession(connector=tcp_connector(current_app.config)) as s:
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

    # currently we don't do queries by GET, can be added when we take on external beacons
    async def _network_beacon_get(self, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        timeout = current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        return await self._network_beacon_call("GET", url, timeout)

    async def _network_beacon_post(self, payload, endpoint=None):
        url = self.api_url if endpoint is None else self.api_url + "/" + endpoint
        timeout = self.request_timeout(payload)
        return await self._network_beacon_call("POST", url, timeout, payload)

    def request_timeout(self, payload=None):
        return (
            current_app.config["NETWORK_VARIANTS_QUERY_TIMEOUT_SECONDS"]
            if self.has_variants_query(payload)
            else current_app.config["NETWORK_DEFAULT_TIMEOUT_SECONDS"]
        )

    @staticmethod
    def has_variants_query(payload):
        if not payload:
            return False
        query = payload.get("requestParameters", {}).get("g_variant")
        return bool(query)


# class ExternalNetworkNode(NetworkBeacon):
#     pass

# Guidelines for adding a non-Bento beacon to the network
#
# Stuff to add to config (config details you will need that are somehow not discoverable):
# - "query_verb" indicating whether this beacon takes queries by GET or POST
#
# - "assemblies" showing which assemblies this beacon contains
#
# - any remapping needed for the request or the response
# - - may need to map between alphanumeric filters and corresponding ontologies
# - - there may be relevant response details in the "info" field, which is a free field in the spec
#
# - any of the various beacon spec choices that are available but hard to discover
# - - "do I use filtering terms from /filtering_terms or from individuals/filtering_terms?"
#
# - any idiosyncracies that deviate from the spec
# - - some beacons may have custom request urls not matching the ones expected in the spec
# - - response format may deviate from the spec for whatever reason
#
# for bento beacons, we can get both "apiVersion" (version of beacon spec) and "version" (version of this implementation)
# from '/overview", which follows the spec for the root endpoint "/"
# But in the spec for /, BOTH "apiVersion" and "version" point to the same thing (the beacon spec version)
# This is an oversight in the spec.
# But both should be available from /service-info, which correctly distinguishes between apiVersion (type.version) and implementation version (version)
# But /service-info is very limited and may be missing details such as logo_url. So external beacons may need multiple calls to get all service details


# adapt queries from the network accordingly
# ... this may require lots of mapping, eg between alphanumeric values and corresponding ontologies


async def new_init_network_service_registry():
    config = current_app.config["NEW_NETWORK_CONFIG"]
    network = config.get("network")  # beacons in this network
    beacons = config.get("beacons")  # info for each beacon
    host_beacon_url = current_app.config["BEACON_BASE_URL"]

    network_beacons_dict: dict[str, NetworkBeacon] = {}
    async_init_calls = []

    for beacon_name in network:
        api_url = beacons.get(beacon_name, {}).get("api_url")
        if api_url == host_beacon_url:
            async_init_calls.append(HostNode.init_beacon(beacon_name, api_url))
        else:
            async_init_calls.append(BentoNetworkNode.init_beacon(beacon_name, api_url))

    current_app.logger.info("making calls")

    results = await asyncio.gather(*async_init_calls, return_exceptions=True)

    current_app.logger.info(results)

    # filter out any failed calls
    registered_beacons = [b for b in results if not isinstance(b, Exception)]

    current_app.logger.info(f"registered {len(registered_beacons)} beacons in network")

    return network_beacons_dict

    # want {"bqc19": <bqc19 beacon obj>, "local": }

    # step 1: create objects for each beacon (this makes obj with url only, no api calls)

    # step 2: init each beacon using asyncio.gather

    # list of function calls, not http calls
    # but should probably make this a list of objects, not methods
    # : list[NetworkBeacon] = []

    # get dict of beacons from config
    # init object for each beacon
    # call beacons for filtering terms, not katsu (this is a change from old method)

    # for bento beacons we can call /overview and get everything we need
    # for non-bento beacons:
    # - call / or /service-info for some stuff, and
    # other stuff can be filled in from config, like
    # assemblies, query verb, or anything that should be in / but is missing, like logourl

    # generate network filtering terms
    # ideally do this from beacons instead of katsu, so format may change
    # old code calls this: make_network_filtering_terms(beacon_dict)
