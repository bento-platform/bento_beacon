from flask import Blueprint, jsonify, current_app
from utils.exceptions import NotImplemented

biosamples = Blueprint("biosamples", __name__)

# TODO

@biosamples.route("/biosamples", methods=['GET', 'POST'])
def get_biosamples():
    raise NotImplemented()

@biosamples.route("/biosamples/<id>", methods=['GET', 'POST'])
def biosamples_by_id(id):
    raise NotImplemented()

@biosamples.route("/biosamples/<id>/g_variants", methods=['GET', 'POST'])
def variants_by_biosample(id):
    raise NotImplemented()

@biosamples.route("/biosamples/<id>/analyses", methods=['GET', 'POST'])
def analyses_by_biosample(id):
    raise NotImplemented()

@biosamples.route("/biosamples/<id>/runs", methods=['GET', 'POST'])
def runs_by_biosample(id):
    raise NotImplemented()
