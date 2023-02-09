import logging
import os
from flask import Flask, current_app, request, g
from urllib.parse import urlunsplit
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

from bento_lib.auth.middleware import AuthxFlaskMiddleware, AuthXException

ENABLE_AUTHX = os.getenv('ENABLE_AUTHX', 'False').lower() in ('true', '1', 't')

REQUEST_SPEC_RELATIVE_PATH = "beacon-v2/framework/json/requests/"

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

# http middleware
if ENABLE_AUTHX:
    oidc_issuer = os.getenv(
        'OIDC_ISSUER', "https://localhost/auth/realms/realm")
    client_id = os.getenv('CLIENT_ID', "abc123")

    authxm = AuthxFlaskMiddleware(oidc_issuer, client_id, oidc_alg="RS256")
    with app.app_context():
        current_app.authx = {}
        current_app.authx['enabled'] = True
        current_app.authx['middleware'] = authxm
else: 
    with app.app_context():
        current_app.authx = {'enabled': False}


@app.before_request
def before_request():
    save_request_data()
    validate_request()


# routes
app.register_blueprint(info)
app.register_blueprint(individuals)
app.register_blueprint(variants)
app.register_blueprint(biosamples)
app.register_blueprint(cohorts)
app.register_blueprint(datasets)


@app.errorhandler(Exception)
def generic_exception_handler(e):
    if isinstance(e, APIException):
        current_app.logger.error(f"API Exception: {e.message}")
        return beacon_error_response(e.message, e.status_code), e.status_code
    if isinstance(e, HTTPException):
        current_app.logger.error(f"HTTP Exception: {e.message}")
        return beacon_error_response(e.name, e.code), e.code
    if isinstance(e, AuthXException):
        if request.path != '/':  # ignore logging root calls (healthcheck spam)
            current_app.logger.error(f"AuthX Exception: {e.message}")
        return beacon_error_response(e.message, e.status_code), e.status_code

    current_app.logger.error(f"Server Error: {e}")
    return beacon_error_response("Server Error", 500), 500
