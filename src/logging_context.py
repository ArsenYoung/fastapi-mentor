import uuid

import structlog


def get_new_request_id() -> str:
    return uuid.uuid4().hex


def bind_request_context(request_id: str) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
    structlog.contextvars.clear_contextvars()
