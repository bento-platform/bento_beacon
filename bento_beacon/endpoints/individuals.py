from flask import Blueprint, current_app, request

individuals = Blueprint("individuals", __name__, url_prefix="/api")



@individuals.route("/individuals", methods=['GET', 'POST'])
def get_individuals():

    # check if valid query
    # check auth

    # call kastsu with dict in request payload
    # call katsu with GET, post is for creating a new individual

    # what endpoint to call with filtering terms? /individuals/search?

    # process katsu repsonse into beacon format
    # return beacon response (or beacon error )

    return {"individuals": "TODO"}


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
