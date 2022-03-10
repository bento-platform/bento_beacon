from urllib.parse import _NetlocResultMixinStr
from flask import request, current_app


# TODO: default request META
# TODO: pull values from spec instead of hardcoding
default_request = {
    "IncludeResultsetResponses": "HIT",
    "pagination": 10
}


def map_beacon_query_to_gohan_query():
    print("map_beacon_query_to_gohan_query()")

    c = current_app.config
    print(c)

    values = request.values
    print(values)

    # RE-MAP COORDINATES!

    return {}


# queries about individuals (rather than variants) are done with filtering terms, not with key-value pairs 
# eg, we never launch a search for {"sex": "female"}
# instead use, eg: {"filters": "PATO_0000383"} (ontology terms preferred)

# Beacon request schema: 
# https://github.com/ga4gh-beacon/beacon-v2-Models/blob/main/BEACON-V2-Model/genomicVariations/requestParameters.json
