import aiohttp
from flask import current_app
from urllib.parse import urlsplit, urlunsplit
from .katsu_utils import katsu_network_call
from .exceptions import APIException
from .http import tcp_connector
from ..authz.headers import auth_header_from_request


DRS_TIMEOUT_SECONDS = 10


def drs_url_components(c):
    return urlsplit(c["DRS_URL"])


async def drs_network_call(path, query):
    c = current_app.config

    base_url_components = drs_url_components(c)
    url = urlunsplit(
        (
            base_url_components.scheme,
            base_url_components.netloc,
            base_url_components.path + path,
            query,
            base_url_components.fragment,
        )
    )

    try:
        async with aiohttp.ClientSession(connector=tcp_connector(c)) as s:
            r = await s.get(url, headers=auth_header_from_request(), timeout=DRS_TIMEOUT_SECONDS)
        drs_response = await r.json()

    # TODO
    # on handover errors, keep returning rest of results instead of throwing api exception
    # add optional note in g and add to beacon response
    # return {}
    except aiohttp.ClientError as e:
        current_app.logger.error(f"drs error: {e}")
        raise APIException(message="error generating handover links")

    return drs_response


async def drs_object_from_filename(filename):
    return await drs_network_call("/search", f"name={filename}")


async def filenames_by_results_set(ids):
    if not ids:
        return {}

    # payload for bento search that returns all experiment filenames in results
    payload = {
        "data_type": "phenopacket",
        "query": ["#in", ["#resolve", "subject", "id"], ["#list", *ids]],
        "output": "values_list",
        "field": ["biosamples", "[item]", "experiment", "[item]", "experiment_results", "[item]", "filename"],
    }

    response = await katsu_network_call(payload)
    results = response.get("results")
    files_by_results_set = {}

    for r in results.keys():
        filenames = results[r].get("matches", [])

        # can filter here if needed by filetype or some other property

        unique_filenames = list(set(filenames))
        files_by_results_set[r] = unique_filenames

    return files_by_results_set


async def drs_link_from_vcf_filename(filename):
    obj = await drs_object_from_filename(filename)
    if not obj:
        return None

    # there may be multiple files with the same filename
    # for now, just return the most recent
    most_recent = sorted(obj, key=lambda entry: entry["created_time"], reverse=True)[0]

    # return any http access, in the future we may want to return other stuff (Globus, htsget, etc)
    access_methods = most_recent.get("access_methods", [])
    http_access = next((a for a in access_methods if a.get("type") in ("http", "https")), None)
    return http_access.get("access_url", {}).get("url") if http_access else None


def vcf_handover_entry(url, note=None):
    entry = {"handoverType": {"id": "NCIT:C172216", "label": "VCF file"}, "url": url}
    # optional field for extra information about this file
    if note:
        entry["note"] = note
    return entry


async def handover_for_ids(ids):
    # ideally we would preserve the mapping between ids and links,
    # but this requires changes in katsu to do well

    handovers = {}

    files_for_results = await filenames_by_results_set(ids)

    for results_set, files in files_for_results.items():
        handovers_this_set = []
        for f in files:
            link = await drs_link_from_vcf_filename(f)
            if link:
                handovers_this_set.append(vcf_handover_entry(link))
        handovers[results_set] = handovers_this_set

    return handovers
