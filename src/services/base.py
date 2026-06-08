import structlog


class BaseService():
    logger = structlog.get_logger()