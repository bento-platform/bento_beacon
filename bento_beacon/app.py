import logging
from flask import Flask
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

app = Flask(__name__)
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
        return beacon_error_response(e.message, e.status_code)
    if isinstance(e, HTTPException):
        return beacon_error_response(e.name, e.code)
    return beacon_error_response("Server Error", 500)
