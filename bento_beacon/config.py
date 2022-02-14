import os

# TODO: beacon auth

class Config:

    # TODO: change to 5000?
    BENTO_URL = os.environ.get("CHORD_URL", "http://127.0.0.1:5001/")

    # TODO: should default to false, not true
    BENTO_DEBUG = os.environ.get("CHORD_DEBUG", True)

    KATSU_BASE_URL = os.environ.get(
        "KATSU_BASE_URL", "https://portal.bentov2.local/api/metadata/api")
    GOHAN_BASE_URL = os.environ.get(
        "GOHAN_BASE_URL", "https://portal.bentov2.local/api/gohan")

    # can be "boolean", "count", or "record"
    # TODO: default should probably be boolean rather than record
    BEACON_GRANULARITY = os.environ.get("BEACON_GRANULARITY", "record")

    GOHAN_TIMEOUT = os.environ.get("GOHAN_TIMEOUT", 60)
    KATSU_TIMEOUT = os.environ.get("KATSU_TIMEOUT", 60)
