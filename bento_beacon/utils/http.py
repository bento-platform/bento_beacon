import aiohttp
from functools import cache
from urllib.parse import urlencode

__all__ = [
    "tcp_connector",
    "process_params",
    "params_str",
]


@cache  # re-use the same instance, since the config object should be the same in many cases
def tcp_connector(c):
    return aiohttp.TCPConnector(ssl=c["BENTO_VALIDATE_SSL"])


# aiohttp refuses to encode bools
def process_params(p: dict[str, str | int | bool | None]):
    return {k: str(v) for k, v in p.items() if v is not None}


def params_str(params: dict[str, str | int | bool | None]) -> str:
    """
    Builds a URL params string from a dictionary, stripping out keys with None values.
    :param params: A dictionary of URL params to build a string for.
    :return: The stringified URL params.
    """
    if params_no_none := process_params(params):
        return f"?{urlencode(params_no_none)}"
    return ""
