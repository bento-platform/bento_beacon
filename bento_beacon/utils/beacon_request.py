from flask import current_app, request, g
import jsonschema
from .exceptions import InvalidQuery
import jwt
import requests
import json
import os

from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

OIDC_ISSUER = os.getenv('OIDC_ISSUER', "https://localhost/auth/realms/realm")
OIDC_WELLKNOWN_URL = OIDC_ISSUER + "/protocol/openid-connect/certs"

r =requests.get(OIDC_WELLKNOWN_URL, verify=False)
jwks=r.json()

# TODO: use RS256 ---
OIDC_ALG="HS256" 

public_keys = jwks["keys"]
rsa_key = [x for x in public_keys if x["alg"]=="RS256"][0]
rsa_cert_str = "-----BEGIN CERTIFICATE-----" + rsa_key['x5c'][0] + "-----END CERTIFICATE-----"
# ---

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

            # TODO: use public-key to validate inbound token
            # jwt.decode(token_str, rsa_cert_str, algorithms=['RS256'])

            # TEMP: validate token manually
            header=jwt.get_unverified_header(token_str)
            payload=jwt.decode(token_str, options={"verify_signature": False})

            print(json.dumps(header, indent=4, separators=(',', ': ')))
            print(json.dumps(payload, indent=4, separators=(',', ': ')))
            
            # TODO: parse out relevant claims/data

            # Validate 'alg' and 'iss'
            alg=header["alg"]
            iss=payload["iss"]
            if alg != OIDC_ALG:
                msg='invalid algorithm'
                print(msg)
                raise jwt.InvalidAlgorithmError(msg)
            if iss != OIDC_ISSUER:
                msg='invalid issuer'
                print(msg)
                raise jwt.InvalidIssuerError(msg)
                



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
