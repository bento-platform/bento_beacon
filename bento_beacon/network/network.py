from flask import current_app, request, Blueprint
from ..utils.exceptions import NotFoundException, APIException
from .network_beacons import init_network_service_registry


network = Blueprint("network", __name__, url_prefix="/network")

# Long-term TODOs:
# handle GET args

# and perhaps standard beacon info endpoints at the network level: /map, /configuration, /service-info etc
# these are only useful if we plan to organize hierarchical networks
# (by e.g. adding our network as a single beacon to another network)


@network.route("")
@network.route("/beacons")
async def beacon_network():
    config = current_app.config["NETWORK_CONFIG"]
    if not config:
        raise APIException("can't find beacon network config")

    results = await init_network_service_registry()

    return results


# returns 404 if endpoint missing
@network.route("/beacons/<beacon_id>/<endpoint>", methods=["GET", "POST"])
async def query(beacon_id, endpoint):
    beacon = current_app.config["NETWORK_BEACONS"].get(beacon_id)

    if not beacon:
        raise NotFoundException(message=f"no beacon found with id {beacon_id}")

    if endpoint not in current_app.config["NETWORK_VALID_QUERY_ENDPOINTS"]:
        raise NotFoundException()

    if request.method == "POST":
        payload = request.get_json()
        r = await beacon.query_beacon(payload, endpoint)
    else:
        # network is post-only for the moment
        raise APIException("network accepts POST only")

    return r
