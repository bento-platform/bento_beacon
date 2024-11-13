import aiohttp

__all__ = ["tcp_connector"]


def tcp_connector(c):
    return aiohttp.TCPConnector(verify_ssl=not c["BENTO_DEBUG"])


# aiohttp refuses to encode bools
def aiohttp_params(p):
    return {k: (str(v) if isinstance(v, bool) else v) for k, v in p.items()}
