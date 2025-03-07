import aiohttp
from json import JSONDecodeError
from flask import current_app
from .exceptions import APIException
from .http import tcp_connector
from ..authz.access import create_access_header_or_fall_back


async def gene_position_lookup(gene_id: str, assembly_id: str) -> dict[str, str | int | None]:
    reference_url = current_app.config["REFERENCE_URL"] + f"/genomes/{assembly_id}/features?name={gene_id}"
    try:
        async with aiohttp.ClientSession(connector=tcp_connector(current_app.config)) as s:
            async with s.get(reference_url, headers=await create_access_header_or_fall_back()) as r:

                if not r.ok:
                    current_app.logger.warning(f"reference service error, status: {r.status_code}, message: {r.text}")
                    raise APIException(message="error searching reference service")
                results = (await r.json()).get("results")

    except JSONDecodeError:
        current_app.logger.error(f"error reading response from reference service")
        raise APIException(message="invalid non-JSON response from reference service")
    except aiohttp.ClientError as e:
        current_app.logger.error(f"reference error: {e}")
        raise APIException(message="error calling reference service")

    if not results:
        return {}

    chromosome = results[0].get("contig_name", "").removeprefix("chr")
    entries = results[0].get("entries")
    start = entries[0].get("start_pos") if entries else None
    end = entries[0].get("end_pos") if entries else None

    return {"chromosome": chromosome, "start": start, "end": end}
