import requests
from flask import Blueprint, jsonify, current_app, request

from ..utils.beacon_response import beacon_response
from ..utils.gohan_utils import gohan_results
from ..utils.exceptions import InvalidQuery, NotImplemented

variants = Blueprint("variants", __name__, url_prefix="/api")


@variants.route("/g_variants", methods=['GET', 'POST'])
def get_variants():
    granularity = current_app.config["BEACON_GRANULARITY"]

    if request.method == "GET":
        beacon_args = request.args.to_dict()
    else:
        beacon_args = request.get_json()

    # print(f"REQUEST VALUES: {request.values}")
    # print(f"PARSED ARGS: {beacon_args}")
    # print(f"REQUEST DATA: {request.get_data()}")
    # print(f"FORM DATA: {request.form.to_dict(flat=False)}")

    # TODO: if filtering terms present, call katsu and join

    results = gohan_results(beacon_args, granularity)

    return beacon_response(results)


@variants.route("/g_variants/<id>", methods=['GET', 'POST'])
def variant_by_id(id):
    # get one variant by (internal) id
    raise NotImplemented()


@variants.route("/g_variants/<id>/biosamples", methods=['GET', 'POST'])
def biosamples_by_variant(id):
    # all biosamples for a particular variant
    raise NotImplemented()


@variants.route("/g_variants/<id>/individuals", methods=['GET', 'POST'])
def individuals_by_variant(id):
    # all individuals for a particular variant
    raise NotImplemented()
