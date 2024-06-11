from flask import current_app, g, request, Blueprint
from json import JSONDecodeError
import requests
from urllib.parse import urlsplit, urlunsplit
from ..utils.exceptions import APIException, NotFoundException
from .utils import beacon_network_response, network_beacon_get, network_beacon_post
from .network_config import VALID_ENDPOINTS, KATSU_CONFIG_UNION, KATSU_CONFIG_INTERSECTION

network = Blueprint("network", __name__)


# TODOs:
# filtering terms XXXXXXXXXXXXXXXXXXXXXXXXXXX
# /service-info? there's already one at beacon root
# async calls

# standard beacon info endpoints at the network level: /map, /configuration, etc
# handle GET args


@network.route("/network")
@network.route("/network/beacons")
def network_beacons():
    beacons = current_app.config["NETWORK_BEACONS"]

    # temp, fake
    filters_union = KATSU_CONFIG_UNION
    filters_intersection = KATSU_CONFIG_INTERSECTION

    return {
        "filtersUnion": filters_union,
        "filtersIntersection": filters_intersection,
        "beacons": list(beacons.values()),
    }


@network.route("/network/query/<endpoint>", methods=["POST"])
def dumb_network_query(endpoint):
    """
    Beacon network query in a single request and single response.
    Returns an aggregate response as well as an array of individual beacon responses.
    As slow as the slowest beacon.
    """
    beacons = current_app.config["NETWORK_BEACONS"]
    if not beacons:
        raise APIException(message="beacon network error, network is empty")

    responses = {}
    for b in beacons:
        url = beacons[b].get("apiUrl")
        try:
            r = network_beacon_post(
                url,
                request.json,
                endpoint,
            )
        except APIException as e:
            r["error"] = {"errorMessage": e.message}
            continue

        # discard beacon "meta" response field
        # it's the same for all requests, including this network request
        r.pop("meta", None)

        responses[b] = r

    if not responses:
        raise APIException(message="No response from beacon network")

    return beacon_network_response(responses)


@network.route("/network/beacons/<beacon_id>")
@network.route("/network/beacons/<beacon_id>/<endpoint>", methods=["GET", "POST"])
def query(beacon_id, endpoint="overview"):
    beacon = current_app.config["NETWORK_BEACONS"].get(beacon_id)
    if not beacon:
        raise NotFoundException(message=f"no beacon found with id {beacon_id}")

    if endpoint not in VALID_ENDPOINTS:
        raise NotFoundException()

    api_url = beacon.get("apiUrl")

    if request.method == "POST":
        payload = request.get_json()
        r = network_beacon_post(api_url, payload, endpoint)
    else:
        # TODO: pass get args
        r = network_beacon_get(api_url, endpoint)

    return r
