from flask import current_app, request, g
import jsonschema
from .exceptions import InvalidQuery


def request_defaults():
    return {
        "apiVersion": current_app.config["BEACON_SPEC_VERSION"],
        "granularity": current_app.config["DEFAULT_GRANULARITY"].get(request.blueprint, None),
        "includeResultsetResponses": "ALL",
        "pagination": {
            "skip": 0,
            "limit": 0
        },
        "requestedSchemas": []
    }


# request read from flask request context
def query_parameters_from_request():
    if request.method == "POST":
        beacon_args = request.get_json() or {}
    else:
        beacon_args = {}

    variants_query = beacon_args.get("query", {}).get(
        "requestParameters", {}).get("g_variant") or {}
    filters = beacon_args.get("query", {}).get("filters") or []

    # reject if too many filters
    max_filters = current_app.config["MAX_FILTERS"]
    if max_filters > 0 and len(filters) > max_filters:
        raise InvalidQuery(
            f"too many filters in request, maximum of {max_filters} permitted")

    phenopacket_filters = list(filter(lambda f: f["id"].startswith("phenopacket."), filters))
    experiment_filters = list(filter(lambda f: f["id"].startswith("experiment."), filters))
    config_filters = [f for f in filters if f not in phenopacket_filters and f not in experiment_filters]
    
    # strip filter prefixes, no longer needed
    phenopacket_filters = list(map(lambda f:  {"id": f["id"][len("phenopacket."):], "operator": f["operator"], "value": f["value"]}, phenopacket_filters))
    experiment_filters = list(map(lambda f:  {"id": f["id"][len("experiment."):], "operator": f["operator"], "value": f["value"]}, experiment_filters))
    return variants_query, phenopacket_filters, experiment_filters, config_filters


def save_request_data():
    defaults = request_defaults()

    # queries only use POST for now
    # if GET, it's a call to an info endpoint, can ignore anything here for now
    if request.method == "POST":
        request_args = request.get_json() or {}
    else:
        request_args = {}

    request_meta = request_args.get("meta", {})
    request_query = request_args.get("query", {})

    request_data = {
        "apiVersion": request_meta.get("apiVersion", defaults["apiVersion"]),
        "requestedSchemas": request_meta.get("requestedSchemas", defaults["requestedSchemas"]),
        "pagination": {**defaults["pagination"], **request_query.get("pagination", {})},
        "requestedGranularity": request_query.get("requestedGranularity", defaults["granularity"])
    }

    g.request_data = request_data


def validate_request():
    if request.method == "POST":
        request_args = request.get_json() or {}
    else:
        # GET currently used for info endpoints only, so no request payload
        return

    # file path resolver for local json schema
    resolver = jsonschema.validators.RefResolver(
        base_uri=current_app.config["BEACON_REQUEST_SPEC_URI"],
        referrer=True,
    )

    try:
        jsonschema.validate(
            instance=request_args,
            schema={"$ref": "beaconRequestBody.json"},
            resolver=resolver,
        )

    except jsonschema.exceptions.ValidationError as e:
        raise InvalidQuery(message=f"Bad Request: {e.message}")

    return
