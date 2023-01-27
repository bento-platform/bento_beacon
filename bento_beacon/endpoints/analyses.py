from flask import Blueprint
from ..utils.exceptions import NotImplemented

analyses = Blueprint("analyses", __name__)


@analyses.route("/analyses", methods=['GET', 'POST'])
def get_analyses():
    # TODO
    raise NotImplemented()


@analyses.route("/analyses/<id>", methods=['GET', 'POST'])
def get_experiment_by_id(id):
    # TODO
    # useful only if we do full-record response here
    raise NotImplemented()


@analyses.route("/analyses/<id>/g_variants", methods=['GET', 'POST'])
def variants_by_experiment(id):
    # possibly redundant to vcf handover
    raise NotImplemented()
