import os

# TODO: beacon auth


class Config:
    BENTO_URL = os.environ.get("CHORD_URL", "http://127.0.0.1:5000/")

    # TODO: should default to false, not true
    BENTO_DEBUG = os.environ.get("CHORD_DEBUG", True)

    # can be "boolean", "count", or "record"
    # TODO: default should probably be boolean rather than record
    BEACON_GRANULARITY = os.environ.get("BEACON_GRANULARITY", "record")

    MAP_EXTRA_PROPERTIES_TO_INFO = os.environ.get(
        "MAP_EXTRA_PROPERTIES_TO_INFO", True)

# -------------------

    KATSU_BASE_URL = os.environ.get(
        "KATSU_BASE_URL", "https://portal.bentov2.local/api/metadata/api")
    KATSU_BIOSAMPLES_ENDPOINT = "/biosamples"
    KATSU_TIMEOUT = os.environ.get("KATSU_TIMEOUT", 60)

# -------------------

    GOHAN_BASE_URL = os.environ.get(
        "GOHAN_BASE_URL", "https://portal.bentov2.local/api/gohan")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_TIMEOUT = os.environ.get("GOHAN_TIMEOUT", 60)
