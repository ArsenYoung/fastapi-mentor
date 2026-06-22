from typing import Any, Mapping, Sequence

import structlog

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException


class BaseService():
    logger = structlog.get_logger()

    def _raise_not_found(
            self,
            message: str | None = None,
            details: Mapping[str, Any] | Sequence[Any] | str | None = None,
            **context
    ) -> None:
        self.logger.warning(
            message or ObjectNotFoundException.message,
            **context,
        )
        raise ObjectNotFoundException(
            message=message,
            details=details,
        )

    def _raise_already_exists(
            self,
            message: str | None = None,
            details: Mapping[str, Any] | Sequence[Any] | str | None = None,
            **context) -> None:
        self.logger.warning(
            message or AlreadyExistsException.message,
            **context,
        )
        raise AlreadyExistsException(
            message=message,
            details=details,
        )
