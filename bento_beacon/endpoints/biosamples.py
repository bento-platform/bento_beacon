from flask import Blueprint,
from ..utils.exceptions import NotImplemented


biosamples = Blueprint("biosamples", __name__)



@biosamples.route("/biosamples", methods=['GET', 'POST'])
def get_biosamples():  # TODO: authz
    raise NotImplemented()


@biosamples.route("/biosamples/<id>", methods=['GET', 'POST'])
def get_katsu_biosamples_by_id(id):  # TODO: authz
    raise NotImplemented()


@biosamples.route("/biosamples/<id>/g_variants", methods=['GET', 'POST'])
def variants_by_biosample(id):  # TODO: authz
    raise NotImplemented()


@biosamples.route("/biosamples/<id>/analyses", methods=['GET', 'POST'])
def analyses_by_biosample(id):  # TODO: authz
    raise NotImplemented()


@biosamples.route("/biosamples/<id>/runs", methods=['GET', 'POST'])
def runs_by_biosample(id):  # TODO: authz
    raise NotImplemented()
