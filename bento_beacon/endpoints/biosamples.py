from json import JSONDecodeError
import requests
from flask import Blueprint, jsonify, current_app, request
from ..utils.exceptions import APIException, NotImplemented
from ..utils.beacon_request import query_parameters_from_request
from ..utils.beacon_response import beacon_response, katsu_not_found
from ..utils.beacon_mappings import katsu_biosample_to_beacon_biosample
from ..utils.katsu_utils import katsu_total_biosamples_count, katsu_filters_query
from ..utils.gohan_utils import query_gohan


biosamples = Blueprint("biosamples", __name__)


@biosamples.route("/biosamples", methods=['GET', 'POST'])
def get_biosamples():
    granularity = current_app.config["BEACON_GRANULARITY"]

    variants_query, filters = query_parameters_from_request()
    sample_ids = []

    # if no query, return total count of biosamples
    if not (variants_query or filters):
        total_count = katsu_total_biosamples_count()
        return beacon_response({"count": total_count})

    if variants_query:
        sample_ids = query_gohan(variants_query, granularity, ids_only=True)
        # skip katsu call if no results
        if not sample_ids:
            return beacon_response({"count": 0})
        # skip katsu call if no filters
        if not filters:
            return beacon_response({"count": len(sample_ids)})

    # else filters in query
    katsu_results = katsu_filters_query(filters, get_biosample_ids=True)

    # TODO: possible overcount in this case
    if not variants_query:
        return beacon_response({"count": katsu_results["count"]})
    
    katsu_ids = katsu_results["results"]
    intersection = list(set(katsu_ids) & set(sample_ids))
    return beacon_response({"count": len(intersection)})


@biosamples.route("/biosamples/<id>", methods=['GET', 'POST'])
def get_katsu_biosamples_by_id(id):
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
