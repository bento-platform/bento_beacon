import logging
from flask import Flask, json
from .endpoints.info import info
from .endpoints.individuals import individuals
from .endpoints.variants import variants
from .endpoints.biosamples import biosamples
from .endpoints.cohorts import cohorts
from .endpoints.datasets import datasets
from .utils.exceptions import APIException
from werkzeug.exceptions import HTTPException
from .config_files.config import Config

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


@app.errorhandler(APIException)
def beacon_exception(e):
    return e.beacon_exception(), e.status_code


@app.errorhandler(HTTPException)
def generic_exception_handler(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response, e.code

# TODO: normalize exceptions so they all return beacon errors, add handler for InternalServerError