import aiohttp

__all__ = ["tcp_connector"]


def tcp_connector(c):
    return aiohttp.TCPConnector(verify_ssl=not c["BENTO_DEBUG"])
