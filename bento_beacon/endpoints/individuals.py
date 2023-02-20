from flask import Blueprint, current_app, g
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response
from ..utils.katsu_utils import katsu_filters_and_sample_ids_query, katsu_filters_query, katsu_total_individuals_count
from ..utils.gohan_utils import query_gohan
from werkzeug.exceptions import HTTPException

from bento_lib.auth.wrappers import authn_token_required_flask_wrapper, authn_token_optional_flask_wrapper

individuals = Blueprint("individuals", __name__)


@individuals.route("/individuals", methods=['GET', 'POST'])
@authn_token_optional_flask_wrapper
def get_individuals():
    granularity = current_app.config["DEFAULT_GRANULARITY"]["individuals"]

    if current_app.authx['enabled'] and g.authn["has_valid_token"]:
        print("xxxxxxxxxxxxxxxxx full response xxxxxxxxxxxxxxxxx")




    # TODO: data access filtering by roles
    # if current_app.authx['enabled']:
    #     print(f"has_valid_token: {g.authn['has_valid_token']}")
    #     print(g.authn['roles'])

    variants_query, filters = query_parameters_from_request()

    # if no query, return total count of individuals
    if not (variants_query or filters):
        total_count = katsu_total_individuals_count()
        return beacon_response({"count": total_count})

    results = {}
    sample_ids = []

    if variants_query:
        sample_ids = query_gohan(variants_query, granularity, ids_only=True)
        print(f"gohan sample ids: {sample_ids}")
        # skip katsu call if no results
        if not sample_ids:
            return beacon_response({"count": 0, "results": []})
        return beacon_response(katsu_filters_and_sample_ids_query(filters, sample_ids))

    # else filters query only
    results = katsu_filters_query(filters)
    print(results)

    return beacon_response(results)


@individuals.route("/individuals/<id>", methods=['GET', 'POST'])
def individual_by_id(id):
    # get one individual by id
    return {"individual by id": "TODO"}


@individuals.route("/individuals/<id>/g_variants", methods=['GET', 'POST'])
def individual_variants(id):
    # all variants for a particular individual
    return {"individual variants": "TODO"}


@individuals.route("/individuals/<id>/biosamples", methods=['GET', 'POST'])
def individual_biosamples(id):
    # all biosamples for a particular individual
    return {"individual biosamples": "TODO"}


@individuals.route("/individuals/<id>/filtering_terms", methods=['GET', 'POST'])
def individual_filtering_terms(id):
    # filtering terms for a particular individual
    return {"individual filtering terms": "TODO"}
