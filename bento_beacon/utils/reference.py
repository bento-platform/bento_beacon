from json import JSONDecodeError
from flask import current_app
from .exceptions import APIException
from ..authz.access import create_access_header_or_fall_back
import requests


def gene_position_lookup(geneId, assemblyId) -> dict[str, str | int | None]:
    reference_url = current_app.config["REFERENCE_URL"] + f"/genomes/{assemblyId}/features?name={geneId}"
    try:
        r = requests.get(
            reference_url,
            headers=create_access_header_or_fall_back(),
            verify=current_app.config["BENTO_VALIDATE_SSL"],
        )

        results = r.json().get("results")
        if not results:
            return {}

        chromosome = results[0].get("contig_name", "").removeprefix("chr")
        entries = results[0].get("entries")
        start = entries[0].get("start_pos") if entries else None
        end = entries[0].get("end_pos") if entries else None

    except JSONDecodeError:
        current_app.logger.error(f"error reading response from reference service")
        raise APIException(message="invalid non-JSON response from katsu")
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"reference service error: {e}")
        raise APIException(message="error calling reference service")

    return {"chromosome": chromosome, "start": start, "end": end}