from msilib import sequence
from urllib.parse import _NetlocResultMixinStr
from flask import request, current_app
from .exceptions import APIException, InvalidQuery

# TODO: default request META
# TODO: pull values from spec instead of hardcoding
BEACON_DEFAULT_REQUEST_ARGS = {
    "IncludeResultsetResponses": "HIT",
    "pagination": 10
}

GOHAN_DEFAULT_REQUEST_ARGS = {

}


# mappings between zero- and one-based coordinates
def zero_to_one(position):
    # TODO
    return position


def one_to_zero(position):
    # TODO
    return position


def gohan_results(beacon_args, granularity):

    gohan_query_args = {}

    # TODO: better control flow

    start = beacon_args.get("start")
    end = beacon_args.get("end")

    numStart = len(start) if start is not None else 0
    numEnd = len(end) if end is not None else 0

    sequence_query = numStart == 1 and numEnd == 0
    range_query = numStart == 1 and numEnd == 1
    bracket_query = numStart == 2 and numEnd == 2

    if not(sequence_query or range_query or bracket_query):
        raise InvalidQuery()

    if bracket_query:
        return bracket_query_to_gohan(beacon_args, granularity)

    elif sequence_query:
        return sequence_query_to_gohan(beacon_args, granularity)

    # else range query, no other cases
    return generic_gohan_query(beacon_args, granularity)


def bracket_query_to_gohan(beacon_args, granularity):
    # TODO
    return {}


def sequence_query_to_gohan(beacon_args, granularity):
    alternateBases = beacon_args.get("alternateBases")
    if alternateBases is None:
        raise InvalidQuery(
            message="variant query requires either 'end' or 'alternateBases' parameters")

    # forward to generic query
    beacon_args["end"] = beacon_args["start"]
    return generic_gohan_query(beacon_args, granularity)


def generic_gohan_query(beacon_args, granularity):
    # TODO

    # expected params:
    # referenceName
    # start
    # end
    # alternateBases
    # referenceBases
    # assemblyId

    # variantType
    # aminoacidChange

    # RE-MAP COORDINATES!

    return {}


def map_beacon_query_to_gohan_query(args):
    print("variant query args:")
    print(args)

    start = args.get("start")
    end = args.get("end")

    numStart = len(start) if start is not None else 0
    numEnd = len(end) if end is not None else 0

    sequence_query = numStart == 1 and numEnd == 0
    range_query = numStart == 1 and numEnd == 1
    bracket_query = numStart == 2 and numEnd == 2

    if not(sequence_query or range_query or bracket_query):
        raise InvalidQuery()

    if bracket_query():

    print(f"len(start)")

    x = args.get("param1")
    print(f"param1 is {x}")

    print(args)

    return {}


def gohan_bracket_query(args):
    return {}


# --------------------------------------------
#     BEACON VARIANT QUERY TYPES
# --------------------------------------------

# Three distinct types of variant query: SEQUENCY QUERY, RANGE QUERY, BRACKET QUERY
# distinguished by the number of "start" and "end" parameters:

#  NUM PARAMS
# START   END     USE
#   1      0      sequence query
#   1      1      range query
#   2      2      bracket query

# ... other combinations of the number of "start" and "end" params are not meaningful


# --------------------------------------------
# "SEQUENCE QUERIES" are for SNPs and small indels
#  "start" represents the start position of the variant

# query params:
#     referenceName
#     start (single value)
#     alternateBases
#     referenceBases
#     (assemblyId)


# example for a single base mutation (G>A) in EIF4A1:

#   "referenceName": "NC_000017.11",
#   "start": [7577120],
#   "referenceBases": "G",
#   "alternateBases": "A"

# Gohan mapping for sequence query
# Gohan requires both "lower bound" and "upper bound", but will accept lower=upper
# Gohan will return variants starting at position p with (lowerBound = upperBound = p) regardless of variant length
# (this still requires remapping from zero-based coordinates)

# GOHAN             BEACON
# assemblyId        assemblyId (optional in beacon, since sometimes contained in "referenceName")
# chromosome        determine from referenceName
# lowerBound        start ***remapped to 1-based***
# upperBound        (set equal to lowerBound)
# reference         referenceBases
# alternative       alternateBases

# + beacon optional params (what's optional here?)


# --------------------------------------------
# RANGE QUERIES return any variant fully or partially overlapping the range between start and end
# here "start" and "end" refer only to start and end of the range to search

# query params:
#     referenceName
#     start (single value)
#     end (single value)
#     optional variantType OR alternateBases OR aminoacidChange
#     optional variantMinLength
#     optional variantMaxLength
#     (assemblyId)

# example: Any variant affecting EIF4A1

#   "referenceName": "NC_000017.11",
#   "start": [ 7572837 ],
#   "end": [ 7578641 ]


# NOTE: I'm assuming here that "any variant falling fully or partially within the range between `start` and `end`"
# means that at least one of variant start and variant end are inside. This ignores for now the possibiilty that the
# variant covers the range, but both starts and ends outside of it. The spec is not precise about this.

# Range queries correspond to a normal gohan search, so:

# GOHAN             BEACON
# lowerBound        start   ***remapped to 1-based***
# upperBound        end     ***remapped to 1-based***
# + other mappings as above

# optional params not supported by gohan: variantMinLength, variantMaxLength, variantType, aminoacidChange
# For all four, the main options are:
# (1) do standard gohan search and filter results in beacon according to params, OR
# (2) implement missing feature in gohan


# --------------------------------------------
# BRACKET QUERIES return variants that have their start and end points inside the ranges given for "start" and "end"
# Bracket queries can also accommodate exact start or end point by setting, eg: start: [n, n+1]
# ... this specifies one position only (since beacon coordinate are half-open)


# query params:
#     referenceName
#     start[min, max] (2 start parameters)
#     end[min, max] (2 end parameters)
#     variantType (optional)
#     (assemblyId)

# what about alternateBases, aminoacidChange? These are optional in Range queries but not here? why not?

# example: CNV Query - TP53 Deletion Query by Coordinates

    # "referenceName": "NC_000017.11",
    # "start": [ 5000000, 7676592 ],
    # "end": [ 7669607, 10000000 ],
    # "variantType": "DEL"


# brackets are not supported by gohan, so as above, the main options are to:
# (1) implement in gohan
# (2) filter results in beacon accordingly (for large ranges, this can be a lot of data, so call gohan paginated)

# mapping, assuming gohan unchanged:

# GOHAN             BEACON
# lowerBound        start[0]   ***remapped to 1-based***
# upperBound        end[1]     ***remapped to 1-based***
#  + as above


# assuming gohan unchanged:
# call all variants
# filter out start and end positions not matching brackets
# filter out variants not matching variant type (when type present)
# **** how to handle type queries when no types in data? ****


# queries about individuals (rather than variants) are done with filtering terms, not with key-value pairs
# eg, we never launch a search for {"sex": "female"}
# instead use, eg: {"filters": "PATO_0000383"} (ontology terms preferred)

# Beacon request schema:
# https://github.com/ga4gh-beacon/beacon-v2-Models/blob/main/BEACON-V2-Model/genomicVariations/requestParameters.json
