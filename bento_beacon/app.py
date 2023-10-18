import logging
import os
from flask import Flask, current_app, request
from time import sleep
from urllib.parse import urlunsplit
from .endpoints.info import info
from .endpoints.individuals import individuals
from .endpoints.variants import variants
from .endpoints.biosamples import biosamples
from .endpoints.cohorts import cohorts
from .endpoints.datasets import datasets
from .utils.exceptions import APIException
from werkzeug.exceptions import HTTPException
from .authz.middleware import authz_middleware
from .config_files.config import Config
from .utils.beacon_response import beacon_error_response
from .utils.beacon_request import save_request_data, validate_request
from .utils.beacon_response import init_response_data
from .utils.katsu_utils import katsu_censorship_settings

REQUEST_SPEC_RELATIVE_PATH = "beacon-v2/framework/json/requests/"
BEACON_MODELS = ["analyses", "biosamples", "cohorts", "datasets", "individuals", "runs", "variants"]

app = Flask(__name__)

# find path for beacon-v2 spec
app_parent_dir = os.path.dirname(app.root_path)
beacon_request_spec_uri = urlunsplit(
    ("file", app_parent_dir, REQUEST_SPEC_RELATIVE_PATH, "", ""))
app.config.from_mapping(
    BEACON_REQUEST_SPEC_URI=beacon_request_spec_uri
)

app.config.from_object(Config)

# all logs are printed in dev mode regardless of level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# attach authz middleware to the Flask app
authz_middleware.attach(app)

# blueprints
# always load info endpoints, load everything else based on config

app.register_blueprint(info)

blueprints = {
    "biosamples": biosamples,
    "cohorts": cohorts,
    "datasets": datasets,
    "individuals": individuals,
    "variants": variants,
}

with app.app_context():
    # load blueprints
    endpoint_sets = current_app.config["BEACON_CONFIG"].get("endpointSets")
    for endpoint_set in endpoint_sets:
        if endpoint_set not in BEACON_MODELS:
            raise APIException(message="beacon config contains unknown endpoint set")
        app.register_blueprint(blueprints[endpoint_set])

    # get censorship settings from katsu
    max_filters = None
    count_threshold = None
    retries = 0
    max_retries = current_app.config["MAX_RETRIES_FOR_CENSORSHIP_PARAMS"]
    for tries in range(max_retries+1):
        current_app.logger.info("calling katsu for censorship parameters")
        try:
            max_filters, count_threshold = katsu_censorship_settings()
        except APIException:
            # katsu down or unavailable, details logged when exception thrown
            # swallow exception and continue retries
            current_app.logger.error("error calling katsu for censorship settings")

        if max_filters is not None and count_threshold is not None:
            break
        sleep(5 + 5*tries)

    # either params retrieved or we hit max retries
    if max_filters is None or count_threshold is None:
        current_app.logger.error("unable to retrieve censorship settings from katsu")
    else:
        current_app.logger.info(
            f"retrieved censorship params: max_filter {max_filters}, count_threshold: {count_threshold}")

    # save even if None
    current_app.config["MAX_FILTERS"] = max_filters
    current_app.config["COUNT_THRESHOLD"] = count_threshold


@app.before_request
def before_request():
    validate_request()
    save_request_data()
    init_response_data()


@app.errorhandler(Exception)
def generic_exception_handler(e):
    # Assume we've determined this exception is OK to show upstream (i.e., not mask with a 403 Forbidden),
    # and mark the request authz as completed.
    authz_middleware.mark_authz_done(request)
    # Situations where we may want to mask, e.g., 404s include situations where a specific ID is involved;
    # if we don't mask 404s there, the IDs in a dataset could be enumerated + guessed.

    if isinstance(e, APIException):
        current_app.logger.error(f"API Exception: {e.message}")
        return beacon_error_response(e.message, e.status_code), e.status_code
    if isinstance(e, HTTPException):
        current_app.logger.error(f"HTTP Exception: {e}")
        return beacon_error_response(e.name, e.code), e.code

    current_app.logger.error(f"Server Error: {e}")
    return beacon_error_response("Server Error", 500), 500
