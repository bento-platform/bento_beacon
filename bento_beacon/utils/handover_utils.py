from flask import current_app
import requests
from urllib.parse import urlsplit, urlunsplit
from .katsu_utils import katsu_network_call
from .exceptions import APIException
from .nested_query_utils import auth_header_from_request


DRS_TIMEOUT_SECONDS = 10


def drs_url_components():
    return urlsplit(current_app.config["DRS_URL"])


def drs_file_link_for_id(id):
    url_components = drs_url_components()
    path = url_components.path + "/objects/" + id + "/download"
    return urlunsplit((
        "https",
        url_components.netloc,
        path,
        url_components.query,
        url_components.fragment
    ))


def drs_network_call(path, query):
    base_url_components = drs_url_components()
    url = urlunsplit((
        base_url_components.scheme,
        base_url_components.netloc,
        base_url_components.path + path,
        query,
        base_url_components.fragment
    ))

    try:
        r = requests.get(
            url,
            headers=auth_header_from_request(),
            timeout=DRS_TIMEOUT_SECONDS,
            verify=not current_app.config.get("BENTO_DEBUG")
        )
        drs_response = r.json()

    # TODO
    # on handover errors, keep returning rest of results instead of throwing api exception
    # add optional note in g and add to beacon response
    # return {}
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"drs error: {e}")
        raise APIException(message="error generating handover links")

    return drs_response


def drs_object_from_filename(filename):
    return drs_network_call("/search", f"name={filename}")


def filenames_by_results_set(ids):
    if not ids:
        return {}

    # payload for bento search that returns all experiment filenames in results
    payload = {
        "data_type": "phenopacket",
        "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]],
        "output": "values_list",
        "field": ["biosamples", "[item]", "experiment", "[item]", "experiment_results", "[item]", "filename"]
    }

    response = katsu_network_call(payload)
    results = response.get("results")
    files_by_results_set = {}

    for r in results.keys():
        filenames = results[r].get("matches", [])

        # can filter here if needed by filetype or some other property

        unique_filenames = list(set(filenames))
        files_by_results_set[r] = unique_filenames

    return files_by_results_set


def drs_link_from_vcf_filename(filename):
    obj = drs_object_from_filename(filename)
    if not obj:
        return None

    # there may be multiple files with the same filename
    # for now, just return the most recent
    ordered_by_most_recent = sorted(
        obj, key=lambda entry: entry['created_time'], reverse=True)
    most_recent_id = ordered_by_most_recent[0].get("id")
    drs_url_for_file = drs_file_link_for_id(most_recent_id)
    return drs_url_for_file


def vcf_handover_entry(url, note=None):
    entry = {"handoverType": {"id": "NCIT:C172216", "label": "VCF file"},
             "url": url}
    # optional field for extra information about this file
    if note:
        entry["note"] = note
    return entry


def handover_for_ids(ids):
    # ideally we would preserve the mapping between ids and links,
    # but this requires changes in katsu to do well

    handovers = {}

    files_for_results = filenames_by_results_set(ids)

    for results_set, files in files_for_results.items():
        handovers_this_set = []
        for f in files:
            link = drs_link_from_vcf_filename(f)
            if link:
                handovers_this_set.append(vcf_handover_entry(link))
        handovers[results_set] = handovers_this_set

    return handovers
