import requests
from flask import Flask, json, jsonify, request, render_template
from endpoints.info import info
from endpoints.individuals import individuals
from endpoints.variants import variants
from endpoints.biosamples import biosamples
from utils.exceptions import APIException
from werkzeug.exceptions import HTTPException
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(info)
app.register_blueprint(individuals)
app.register_blueprint(variants)
app.register_blueprint(biosamples)


@app.errorhandler(APIException)
def beacon_exception(e):
    return e.beacon_exception(), e.status_code or 500

# return beacon error json instead of default flask html template
# TODO: use becaon error spec:
# https://github.com/ga4gh-beacon/beacon-framework-v2/blob/main/responses/beaconErrorResponse.json


@app.errorhandler(HTTPException)
def generic_exception_handler(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


# TODO: handle unexpected api errors
# TODO: all routes should start with "/api"
# TODO: take port from config, remove hardcoded debug
app.run(port=5001, debug=True)
