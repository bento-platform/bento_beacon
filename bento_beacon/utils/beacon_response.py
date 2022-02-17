from flask import current_app
from ..service_info import SERVICE_INFO


def map_gohan_response_to_beacon_reponse(r):
    pass


def map_katsu_response_to_beacon_response():
    pass


# Beacon schema for individuals"
# https://github.com/ga4gh-beacon/beacon-v2-Models/blob/main/BEACON-V2-Model/individuals/defaultSchema.json

# beacons can also return phenopackets on request

def beacon_response(results):
    return {
        "meta": build_response_meta(),
        "response": build_response_details(results),
        "responseSummary": build_response_summary(results)
    }


def build_response_meta():
    # -------------------
    # TODO, parameterize all
    returned_schemas = {}
    returned_granularity = current_app.config["BEACON_GRANULARITY"]
    received_request_summary = {}
    # --------------------
    return {
        "beaconId": SERVICE_INFO["id"],
        "apiVersion": SERVICE_INFO["version"],
        "returnedSchemas": returned_schemas,
        "returnedGranularity": returned_granularity,
        "receivedRequestSummary": received_request_summary
    }


def build_response_details(results):
    # TODO: remap response to beacon format
    return results


def build_response_summary(results):

    # ---------------------
    # TODOs, compute from response
    exists = True
    count = -1
    # only "exists" field is required, 
    # can hide count if it's below some threshold for re-identification attack
    # ----------------------
    return {
        "exists": exists,
        "count": count,
    }
