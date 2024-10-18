from flask import current_app
import requests
from .exceptions import APIException, InvalidQuery, NotImplemented
from ..authz.access import create_access_header_or_fall_back
from .reference import gene_position_lookup

# -------------------------------------------------------
#       query mapping
# -------------------------------------------------------

gohan_beacon_variant_query_mapped_fields = {
    "referenceBases": "reference",
    "alternateBases": "alternative",
    "assemblyId": "assemblyId",
    "referenceName": "chromosome",  # could handle accession numbers here, Redmine #1076
}

# throw warning if beacon query includes these terms
# TODO: remove any lines for features that get implemented
beacon_variant_query_not_implemented_params = [
    "variantType",
    "variantMinLength",
    "variantMaxLength",
    "mateName",
    "aminoacidChange",
    "genomicAlleleShortForm",
]


def beacon_to_gohan_generic_mapping(obj):
    gohan_query = {}

    for beacon_key, beacon_value in obj.items():
        if beacon_key in gohan_beacon_variant_query_mapped_fields.keys():
            gohan_query[gohan_beacon_variant_query_mapped_fields[beacon_key]] = beacon_value
        elif beacon_key in beacon_variant_query_not_implemented_params:
            raise NotImplemented(f"queries with {beacon_key} not implemented")

    return gohan_query


# -------------------------------------------------------
#       coordinate mapping
# -------------------------------------------------------


# TODO: INS issues, see notes
def zero_to_one(start, end=None):
    return int(start) + 1 if end is None else (int(start) + 1, end)


def one_to_zero(start, end):
    return (int(start) - 1, end)


# -------------------------------------------------------
#       gohan calls
# -------------------------------------------------------


def query_gohan(beacon_args, granularity, ids_only=False):
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

    if geneId_query:
        if start is not None or end is not None:
            raise InvalidQuery("invalid mix of geneId and start/end parameters")
        return geneId_query_to_gohan(beacon_args, granularity, ids_only)

    # required everywhere except geneId query
    if beacon_args.get("referenceName") is None:
        raise InvalidQuery(message="referenceName parameter required")

    if sequence_query:
        return sequence_query_to_gohan(beacon_args, granularity, ids_only)

    if range_query:
        return range_query_to_gohan(beacon_args, granularity, ids_only)

    if bracket_query:
        return bracket_query_to_gohan(beacon_args, granularity, ids_only)

    # no other cases
    raise InvalidQuery()


def sequence_query_to_gohan(beacon_args, granularity, ids_only):
    current_app.logger.debug("SEQUENCE QUERY")
    gohan_args = beacon_to_gohan_generic_mapping(beacon_args)

    alternateBases = beacon_args.get("alternateBases")
    if alternateBases is None:
        raise InvalidQuery(message="variant query requires either 'end' or 'alternateBases' parameters")

    referenceBases = beacon_args.get("referenceBases")
    if referenceBases is None:
        raise InvalidQuery(message="variant sequence query requires 'referenceBases' parameter")

    gohan_args["lowerBound"] = zero_to_one(beacon_args["start"][0])
    gohan_args["upperBound"] = gohan_args["lowerBound"]
    gohan_args["getSampleIdsOnly"] = ids_only

    return generic_gohan_query(gohan_args, granularity, ids_only)


# optional params
# variantType OR alternateBases OR aminoacidChange
# variantMinLength
# variantMaxLength
def range_query_to_gohan(beacon_args, granularity, ids_only):
    current_app.logger.debug("RANGE QUERY")
    gohan_args = beacon_to_gohan_generic_mapping(beacon_args)
    gohan_args["lowerBound"] = zero_to_one(beacon_args["start"][0])
    gohan_args["upperBound"] = zero_to_one(beacon_args["end"][0])
    gohan_args["getSampleIdsOnly"] = ids_only
    return generic_gohan_query(gohan_args, granularity, ids_only)


def bracket_query_to_gohan(beacon_args, granularity, ids_only):
    current_app.logger.debug("BRACKET QUERY")
    # TODO
    # either implement here by filtering full results, or implement directly in gohan
    raise NotImplemented(message="variant bracket query not implemented")


def geneId_query_to_gohan(beacon_args, granularity, ids_only):
    current_app.logger.debug("GENE ID QUERY")
    gene_id = beacon_args.get("geneId")
    assembly_from_query = beacon_args.get("assemblyId")

    # query all assemblies present in gohan if not specified
    assemblies = [assembly_from_query] if assembly_from_query is not None else gohan_assemblies()
    gohan_args = beacon_to_gohan_generic_mapping(beacon_args)

    gohan_results = []
    # TODO: async
    for assembly in assemblies:
        gene_info = gene_position_lookup(gene_id, assembly)
        if not gene_info:
            continue

        gohan_args_this_query = {
            **gohan_args,
            "assemblyId": assembly,
            "chromosome": gene_info.get("chromosome"),
            "lowerBound": gene_info.get("start"),
            "upperBound": gene_info.get("end"),
            "getSampleIdsOnly": ids_only,
        }

        gohan_results.extend(generic_gohan_query(gohan_args_this_query, granularity, ids_only))

    return gohan_results


def generic_gohan_query(gohan_args, granularity, ids_only):
    if ids_only:
        return gohan_ids_only_query(gohan_args, granularity)

    if granularity == "record":
        return gohan_full_record_query(gohan_args)

    # count or boolean query follows
    config = current_app.config
    query_url = config["GOHAN_BASE_URL"] + config["GOHAN_COUNT_ENDPOINT"]
    current_app.logger.debug(f"launching gohan query: {gohan_args}")
    results = gohan_results(query_url, gohan_args)
    count = results.get("count") if results else None
    return {"count": count}


def gohan_ids_only_query(gohan_args, granularity):
    config = current_app.config
    query_url = config["GOHAN_BASE_URL"] + config["GOHAN_SEARCH_ENDPOINT"]
    current_app.logger.debug(f"launching gohan query: {gohan_args}")
    results = gohan_results(query_url, gohan_args)
    return unpackage_sample_ids(results)


def unpackage_sample_ids(results):
    calls = results.get("calls") if results else []
    return list(map(lambda r: r.get("sample_id"), calls))


def gohan_results(url, gohan_args):
    response = gohan_network_call(url, gohan_args)
    results_array = response.get("results")
    results = results_array[0] if results_array else None
    return results


def gohan_network_call(url, gohan_args):
    c = current_app.config

    try:
        r = requests.get(
            url,
            headers=create_access_header_or_fall_back(),
            params=gohan_args,
            timeout=c["GOHAN_TIMEOUT"],
            verify=c["BENTO_VALIDATE_SSL"],
        )

        # handle gohan errors or any bad responses
        if not r.ok:
            current_app.logger.warning(f"gohan error, status: {r.status_code}, message: {r.text}")
            raise APIException(message="error searching gohan variants service")

        gohan_response = r.json()

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"gohan error: {e}")
        raise APIException(message="error calling gohan variants service")

    return gohan_response


# currently used internally only
def gohan_full_record_query(gohan_args):
    config = current_app.config
    query_url = config["GOHAN_BASE_URL"] + config["GOHAN_SEARCH_ENDPOINT"]
    response = gohan_results(query_url, gohan_args)
    return response.get("calls")


def gohan_overview():
    config = current_app.config
    url = config["GOHAN_BASE_URL"] + config["GOHAN_OVERVIEW_ENDPOINT"]
    return gohan_network_call(url, {})


def gohan_totals_by_sample_id():
    return gohan_overview().get("sampleIDs", {})


def gohan_total_variants_count():
    totals_by_id = gohan_totals_by_sample_id()
    return sum(totals_by_id.values())


def gohan_counts_by_assembly_id():
    return gohan_overview().get("assemblyIDs", {})


def gohan_assemblies():
    return list(gohan_overview().get("assemblyIDs", {}).keys())


# only runs if "useGohan" true
def gohan_counts_for_overview():
    return gohan_counts_by_assembly_id()


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
# a fourth query type, GENE ID SEARCH, uses a gene symbol insted of numeric stop/start positions


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
# ... seems like this is a docs issue, the spec itself does not mark any of these values are required or optional

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


# --------------------------------------------
# GENE ID QUERY is a variant of range query
# takes an HGNC gene symbol instead of numeric stop/start positions

# query params:
#     geneId
# optional params:
#     variantType OR alternateBases OR aminoacidChange
#     variantMinLength
#     variantMaxLength

# obviously assemblyId may be useful here as well as an optional parameter, although docs ignore it
