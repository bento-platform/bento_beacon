import logging
import structlog.stdlib
from bento_lib.service_info.manager import ServiceManager

from .exceptions import APIException
from ..config_files.config import BENTO_VALIDATE_SSL, BENTO_SERVICE_REGISTRY_URL

__all__ = ["service_manager", "get_service_url_or_raise"]

service_manager = ServiceManager(
    logger=structlog.stdlib.get_logger("bento_beacon.service_manager"),  # TODO: unified logging
    request_timeout=30,
    service_registry_url=BENTO_SERVICE_REGISTRY_URL,
    verify_ssl=BENTO_VALIDATE_SSL,
)


async def get_service_url_or_raise(kind: str, logger: logging.Logger | structlog.stdlib.BoundLogger):
    service_url = await service_manager.get_bento_service_url_by_kind(kind)
    if service_url is None:
        err = f"could not get service URL from service registry ({kind})"
        logger.error(f"service manager error: {err}")
        raise APIException(message=err)


# TODO: need to mock service manager for tests
