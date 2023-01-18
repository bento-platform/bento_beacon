import logging
from flask import Flask, current_app
from .endpoints.info import info
from .endpoints.individuals import individuals
from .endpoints.variants import variants
from .endpoints.biosamples import biosamples
from .endpoints.cohorts import cohorts
from .endpoints.datasets import datasets
from .utils.exceptions import APIException
from werkzeug.exceptions import HTTPException
from .config_files.config import Config
from .utils.beacon_response import beacon_error_response
from .utils.beacon_request import save_request_data, validate_request

app = Flask(__name__)
app.config.from_mapping(
    ROOT_PATH=app.root_path
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


app.register_blueprint(info)
app.register_blueprint(individuals)
app.register_blueprint(variants)
app.register_blueprint(biosamples)
app.register_blueprint(cohorts)
app.register_blueprint(datasets)


@app.errorhandler(Exception)
def generic_exception_handler(e):
    if isinstance(e, APIException):
        current_app.logger.error(f"API Exception: {e}")
        return beacon_error_response(e.message, e.status_code), e.status_code
    if isinstance(e, HTTPException):
        current_app.logger.error(f"HTTP Exception: {e}")
        return beacon_error_response(e.name, e.code), e.code

    current_app.logger.error(f"Server Error: {e}")
    return beacon_error_response("Server Error", 500), 500


@app.before_request
def before_request():
    save_request_data()
    validate_request()
