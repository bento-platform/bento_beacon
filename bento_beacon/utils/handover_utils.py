from flask import current_app, request, url_for
import requests
from json import JSONDecodeError
from urllib.parse import urlsplit, urlunsplit
from .katsu_utils import katsu_network_call
from .exceptions import APIException

TRUNCATED_BY_GATEWAY = "api/beacon"
DRS_TIMEOUT_SECONDS = 10


def get_handover_url():
    base_url_components = urlsplit(request.url)
    handover_scheme = "https"
    handover_path = TRUNCATED_BY_GATEWAY + url_for("handover.get_handover")
    handover_base_url = urlunsplit((
        handover_scheme,
        base_url_components.netloc,
        handover_path,
        base_url_components.query,
        base_url_components.fragment
    ))
    return handover_base_url


def drs_network_call(path, query):
    base_url_components = urlsplit(current_app.config["DRS_BASE_URL"])
    url = urlunsplit((
        base_url_components.scheme,
        base_url_components.netloc,
        path,
        query,
        base_url_components.fragment
    ))
    print(url)

    try:
        r = requests.get(
            url,
            verify=not c["DEBUG"],
            timeout=DRS_TIMEOUT_SECONDS,
        )
        drs_response = r.json()

    except (JSONDecodeError, requests.RequestException):
        current_app.logger.debug("drs error")
        raise APIException(message="error calling DRS")

    return drs_response


def drs_object_from_filename(filename):
    response = drs_network_call("/search", f"name={filename}")
    print(response)
    pass


def vcf_filenames_from_ids(ids):
    if not ids:
        return []
    payload = {
        "data_type": "phenopacket",
        "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]],
        "output": "values_list",
        "field": ["biosamples", "[item]", "experiment", "[item]", "experiment_results", "[item]", "filename"]
    }
    response = katsu_network_call(payload)
    results = response.get("results")

    all_files = []
    # possibly multiple tables
    for value in results.values():
        if value.get("data_type") == "phenopacket":
            all_files = all_files + value.get("matches")

    # TODO: filter by file type? (vcf, cram, etc) or some other property 
    print(all_files)
    
    return all_files


def drs_link_from_vcf_filename(filename):
    # generate https link 
    pass

