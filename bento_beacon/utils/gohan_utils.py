from flask import request, current_app
from .exceptions import APIException, InvalidQuery, NotImplemented
from json import JSONDecodeError
import requests
from urllib.parse import urljoin

gohan_beacon_variant_query_mapped_fields = {
    "referenceBases":  "reference",
    "alternateBases": "alternative",
    "assemblyId": "assemblyId",
    "referenceName": "chromosome"   # TODO: handle accession numbers here, Redmine #1076
}

# throw warning if beacon query includes these terms
# TODO: remove any lines for features that get implemented
beacon_variant_query_not_implemented_params = [
    "variantType",
    "variantMinLength",
    "variantMaxLength",
    "mateName",
    "geneId",
    "aminoacidChange",
    "genomicAlleleShortForm"
]


def beacon_to_gohan_generic_mapping(obj):
    gohan_query = {}

    for beacon_key, beacon_value in obj.items():
        if beacon_key in gohan_beacon_variant_query_mapped_fields.keys():
            gohan_query[gohan_beacon_variant_query_mapped_fields[beacon_key]] = beacon_value
        elif beacon_key in beacon_variant_query_not_implemented_params:
            raise NotImplemented(
                f"queries with {beacon_key} not implemented")

    return gohan_query


# ------------------------------------------------
# mappings between zero- and one-based coordinates
# TODO: INS issues, see notes

def zero_to_one(start, end=None):
    return int(start)+1 if end is None else (int(start)+1, end)


def one_to_zero(start, end):
    return (int(start)-1, end)

# ------------------------------------------------

# TODO: validate query against spec
def gohan_results(beacon_args, granularity, ids_only=False):

    if beacon_args.get("referenceName") is None:
        raise InvalidQuery(message="referenceName parameter required")

    # control flow for beacon variant query types
    # http://docs.genomebeacons.org/variant-queries/
    start = beacon_args.get("start")
    end = beacon_args.get("end")
    geneId = beacon_args.get("geneId")

    numStart = len(start) if start is not None else 0
    numEnd = len(end) if end is not None else 0

    sequence_query = numStart == 1 and numEnd == 0
    range_query = numStart == 1 and numEnd == 1
    bracket_query = numStart == 2 and numEnd == 2
    geneId_query = geneId is not None

    if not(sequence_query or range_query or bracket_query or geneId_query):
        raise InvalidQuery()

    if bracket_query:
        return bracket_query_to_gohan(beacon_args, granularity, ids_only)

    if sequence_query:
        return sequence_query_to_gohan(beacon_args, granularity, ids_only)

    if geneId_query:
        return geneId_query_to_gohan(beacon_args, granularity, ids_only)

    # else range query, no other cases
    return range_query_to_gohan(beacon_args, granularity, ids_only)


def sequence_query_to_gohan(beacon_args, granularity, ids_only):
    print("SEQUENCE QUERY")
    gohan_args = beacon_to_gohan_generic_mapping(beacon_args)

    alternateBases = beacon_args.get("alternateBases")
    if alternateBases is None:
        raise InvalidQuery(
            message="variant query requires either 'end' or 'alternateBases' parameters")

    referenceBases = beacon_args.get("referenceBases")
    if referenceBases is None:
        raise InvalidQuery(
            message="variant sequence query requires 'referenceBases' parameter")

    gohan_args["lowerBound"] = zero_to_one(beacon_args["start"][0])
    gohan_args["upperBound"] = gohan_args["lowerBound"]
    gohan_args["getSampleIdsOnly"] = ids_only

    return generic_gohan_query(gohan_args, granularity, ids_only)


# optional params
# variantType OR alternateBases OR aminoacidChange
# variantMinLength
# variantMaxLength
def range_query_to_gohan(beacon_args, granularity, ids_only):
    print("RANGE QUERY")
    gohan_args = beacon_to_gohan_generic_mapping(beacon_args)
    gohan_args["lowerBound"] = zero_to_one(beacon_args["start"][0])
    gohan_args["upperBound"] = zero_to_one(beacon_args["end"][0])
    gohan_args["getSampleIdsOnly"] = ids_only
    return generic_gohan_query(gohan_args, granularity, ids_only)


def bracket_query_to_gohan(beacon_args, granularity, ids_only):
    print("BRACKET QUERY")
    # TODO
    # either implement here by filtering full results, or implement directly in gohan
    raise NotImplemented(message="variant bracket query not implemented")


def geneId_query_to_gohan(beacon_args, granularity, ids_only):
    print("GENE ID QUERY")
    # TODO
    # determine assembly, call gohan for gene coordinates, launch search
    raise NotImplemented(message="variant geneId query not implemented")


def generic_gohan_query(gohan_args, granularity, ids_only):
    if (ids_only):
        return gohan_ids_only_query(gohan_args, granularity)

    if granularity == "record":
        return gohan_full_record_query(gohan_args)

    # count or boolean query follows
    config = current_app.config
    query_url = config["GOHAN_BASE_URL"] + config["GOHAN_COUNT_ENDPOINT"]
    current_app.logger.debug(f"launching gohan query: {gohan_args}")
    results = gohan_network_call(query_url, gohan_args)
    count = results.get("count") if results else None
    return {"count": count}


def gohan_ids_only_query(gohan_args, granularity):
    config = current_app.config
    query_url = config["GOHAN_BASE_URL"] + config["GOHAN_SEARCH_ENDPOINT"]
    current_app.logger.debug(f"launching gohan query: {gohan_args}")
    results = gohan_network_call(query_url, gohan_args)
    return unpackage_sample_ids(results)


def unpackage_sample_ids(results):
    calls = results.get("calls") if results else []
    return list(map(lambda r: r.get("sample_id"), calls))


def gohan_network_call(url, gohan_args):
    c = current_app.config
    try:
        r = requests.get(
            url,
            verify=not c["BENTO_DEBUG"],
            timeout=c["GOHAN_TIMEOUT"],
            params=gohan_args
        )

        gohan_response = r.json()
        results_array = gohan_response.get("results")
        results = results_array[0] if results_array else None

        # handle gohan errors or any bad responses
        if not r.ok:
            current_app.logger.warning(
                f"gohan error, status: {r.status_code}, message: {gohan_response.get('message')}")
            raise APIException(
                message=f"error searching gohan variants service: {gohan_response.get('message')}")

    except JSONDecodeError as e:
        current_app.logger.debug(f"gohan error: {e.msg}")
        raise APIException()

    return results


def gohan_full_record_query(gohan_args):
    # TODO
    # return results wrapped in this shape:
    # { count: xx, results: [] }

    raise NotImplemented("full record variant query not implemented")


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

# + beacon optional params


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

# NOTE: the beacon spec says range search should return "any variant with at least partial overlap",
# but does not give a specific definition of overlap. Gohan by default ignores variant length and
# considers only whether the start of the variant is inside the range. This will include some overlapping
# variants and exclude others.

# Otherwise, range queries correspond to a normal gohan search, so:

# GOHAN             BEACON
# lowerBound        start   ***remapped to 1-based***
# upperBound        end     ***remapped to 1-based***
# + other mappings as in sequence query above

# optional params not supported by gohan: variantMinLength, variantMaxLength, variantType, aminoacidChange
# For all four, the main options are:
# (1) do standard gohan search and filter results in beacon according to params, OR
# (2) implement missing feature in gohan


# --------------------------------------------
# BRACKET QUERIES return variants that have their start and end points inside the ranges given for "start" and "end"
# Bracket queries can also accommodate exact start or end point by setting, eg: start: [n, n+1]
# ... this specifies one position only (since beacon coordinates are half-open)

# query params:
#     referenceName
#     start[min, max] (2 start parameters)
#     end[min, max] (2 end parameters)
#     variantType (optional)
#     (assemblyId)

# what about alternateBases, aminoacidChange? These are optional in range queries but not here? why not?

# brackets are not supported by gohan, so as above, the main options are to:
# (1) implement in gohan
# (2) filter results in beacon accordingly (for large ranges, this can be a lot of data, so call gohan paginated)

# mapping, assuming option 2:

# GOHAN             BEACON
# lowerBound        start[0]   ***remapped to 1-based***
# upperBound        end[1]     ***remapped to 1-based***
#  + as above

# assuming gohan unchanged:
# call all matching variants between lowerBound, upperBound
# filter out start and end positions not matching brackets
# filter out variants not matching variant type (when type present)
