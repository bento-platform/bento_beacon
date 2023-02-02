from flask import current_app, request, g
import jsonschema
from .exceptions import InvalidQuery
import jwt

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

def authx_check():
    print("authx checkup")
    if request.headers.get("Authorization"):
        print("authz header discovered")
        # Assume is Bearer token
        authz_str_split=request.headers.get("Authorization").split(' ')
        if len(authz_str_split) > 1:
            token_str = authz_str_split[1]
            print(token_str)

            # TODO: parse out relevant claims/data
            jwt.decode(token_str, "your-256-bit-secret", algorithms=["HS256"])

# request read from flask request context
def query_parameters_from_request():
    if request.method == "POST":
        beacon_args = request.get_json() or {}
    else:
        beacon_args = {}

    variants_query = beacon_args.get("query", {}).get(
        "requestParameters", {}).get("g_variant") or {}
    filters = beacon_args.get("query", {}).get("filters") or []
    return variants_query, filters


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
