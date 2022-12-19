from flask import current_app, request, g


def save_request_data():
    defaults = {
        "apiVersion": current_app.config["BEACON_API_VERSION"],
        "granularity": current_app.config["BEACON_GRANULARITY"],
        "includeResultsetResponses": "ALL",
        "pagination": {
            "skip": 0,
            "limit": 0
        },
        "requestedSchemas": []
    }

    # queries only use POST for now
    # if GET, it's a call to an info endpoint, so just use default values
    if request.method == "POST":
        request_args = request.get_json() or {}
    else:
        request_args = {}

    request_meta = request_args.get("meta", {})
    request_query = request_args.get("query", {})

    # save values to flask global per-request dict
    g.requested_api_version = request_meta.get("apiVersion", defaults["apiVersion"])
    g.requested_schemas = request_meta.get("requestedSchemas", defaults["requestedSchemas"])
    g.requested_pagination = {**defaults["pagination"], **request_query.get("pagination", {})}
    g.requested_granularity = request_query.get("requestedGranularity", defaults["granularity"])

