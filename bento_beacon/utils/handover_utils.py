from flask import current_app, request, url_for
import requests
from urllib.parse import urlsplit, urlunsplit
from .katsu_utils import katsu_network_call
from .exceptions import APIException

# path elements removed by bento gateway
# BEACON_PATH_FRAGMENT = "api/beacon"

DRS_TIMEOUT_SECONDS = 10

# may or may not be needed
# def get_handover_url():
#     base_url_components = urlsplit(request.url)
#     handover_scheme = "https"
#     handover_path = BEACON_PATH_FRAGMENT + url_for("handover.get_handover")
#     handover_base_url = urlunsplit((
#         handover_scheme,
#         base_url_components.netloc,
#         handover_path,
#         base_url_components.query,
#         base_url_components.fragment
#     ))
#     return handover_base_url


def drs_internal_url_components():
    return urlsplit(current_app.config["DRS_INTERNAL_URL"])


def drs_external_url_components():
    return urlsplit(current_app.config["DRS_EXTERNAL_URL"])

# TODO: either remove or deduplicate with below
# def drs_internal_file_link_for_id(id):
#     internal_url_components = drs_internal_url_components()
#     path = internal_url_components.path + "/objects/" + id + "/download"
#     return urlunsplit((
#         internal_url_components.scheme,
#         internal_url_components.netloc,
#         path,
#         internal_url_components.query,
#         internal_url_components.fragment
#     ))


def drs_external_file_link_for_id(id):
    external_url_components = drs_external_url_components()
    path = external_url_components.path + "/objects/" + id + "/download"
    return urlunsplit((
        "https",
        external_url_components.netloc,
        path,
        external_url_components.query,
        external_url_components.fragment
    ))


def drs_network_call(path, query):
    base_url_components = drs_internal_url_components()
    url = urlunsplit((
        base_url_components.scheme,
        base_url_components.netloc,
        path,
        query,
        base_url_components.fragment
    ))

    try:
        r = requests.get(
            url,
            verify=not current_app.config["DEBUG"],
            timeout=DRS_TIMEOUT_SECONDS,
        )
        drs_response = r.json()

    except requests.exceptions.RequestException as e:
        current_app.logger.debug(f"drs error: {e.msg}")
        raise APIException(message="error generating handover links")

    return drs_response


def drs_object_from_filename(filename):
    response = drs_network_call("/search", f"name={filename}")

    # if nothing return None

    print(response)
    return response


def filenames_from_ids(ids):
    if not ids:
        return []

    # payload for bento search that returns all experiment filenames in results
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
    return all_files


def drs_link_from_vcf_filename(filename):
    obj = drs_object_from_filename(filename)
    if not obj:
        return None

    # even with checksum de-duplication, there may be multiple files with the same filename
    # (... perhaps you fixed the sample id in the vcf... )
    # for now, just return the most recent
    ordered_by_most_recent = sorted(
        obj, key=lambda entry: entry['created_time'], reverse=True)
    most_recent_id = ordered_by_most_recent[1].get("id")
    # internal_url = drs_internal_file_link_for_id(most_recent_id)
    external_url = drs_external_file_link_for_id(most_recent_id)
    return external_url


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
    handovers = []
    filenames = filenames_from_ids(ids)
    for f in filenames:
        link = drs_link_from_vcf_filename(f)
        if link:
            handovers.append(vcf_handover_entry(link))
    return handovers
