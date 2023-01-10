from flask import current_app, request, g
import jsonschema
from .exceptions import InvalidQuery


def request_defaults():
    return {
        "apiVersion": current_app.config["BEACON_API_VERSION"],
        "granularity": current_app.config["BEACON_GRANULARITY"],
        "includeResultsetResponses": "ALL",
        "pagination": {
            "skip": 0,
            "limit": 0
        },
        "requestedSchemas": []
    }


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
        base_uri=current_app.config["REQUEST_SCHEMA_URI"],
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
