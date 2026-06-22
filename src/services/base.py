import structlog

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.schemas.errors import ErrorDetailsType


class BaseService():
    logger = structlog.get_logger()

    def _raise_not_found(
            self,
            message: str | None = None,
            details: ErrorDetailsType = None,
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
            details: ErrorDetailsType = None,
            **context) -> None:
        self.logger.warning(
            message or AlreadyExistsException.message,
            **context,
        )
        raise AlreadyExistsException(
            message=message,
            details=details,
        )
