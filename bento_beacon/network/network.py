from flask import current_app, request, Blueprint
from ..utils.exceptions import APIException, NotFoundException
from .utils import network_beacon_get, network_beacon_post, host_beacon_response, filters_intersection, filters_union

network = Blueprint("network", __name__, url_prefix="/network")


# TODOs:
# filtering terms XXXXXXXXXXXXXXXXXXXXXXXXXXX
# /service-info? there's already one at beacon root
# async calls

# standard beacon info endpoints at the network level: /map, /configuration, etc
# handle GET args


@network.route("")
@network.route("/beacons")
def network_beacons():
    beacons_dict = current_app.config.get("NETWORK_BEACONS")
    if not beacons_dict:
        raise APIException("no beacons found in network config")

    # filters handling still experimental
    return {
        "filtersUnion": current_app.config["ALL_NETWORK_FILTERS"],
        "filtersIntersection": current_app.config["COMMON_NETWORK_FILTERS"],
        "beacons": list(beacons_dict.values()),
    }


# returns 404 if endpoint missing
@network.route("/beacons/<beacon_id>/<endpoint>", methods=["GET", "POST"])
def query(beacon_id, endpoint):
    beacon = current_app.config["NETWORK_BEACONS"].get(beacon_id)

    if not beacon:
        raise NotFoundException(message=f"no beacon found with id {beacon_id}")

    if endpoint not in current_app.config["NETWORK_VALID_QUERY_ENDPOINTS"]:
        raise NotFoundException()

    # special handling for host beacon, avoid circular http calls
    host_id = current_app.config["BEACON_ID"]
    if beacon_id == host_id:
        return host_beacon_response(endpoint)

    # all other beacons
    api_url = beacon.get("apiUrl")

    if request.method == "POST":
        payload = request.get_json()
        r = network_beacon_post(api_url, payload, endpoint)
    else:
        # TODO: pass get args
        r = network_beacon_get(api_url, endpoint)

    return r
