from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
import structlog


class BaseService():
    logger = structlog.get_logger()

    def _raise_not_found(
            self,
            message: str = "Object not found",
            **context
    ) -> None:
        self.logger.warning(
            message,
            **context,
        )
        raise ObjectNotFoundException(message)

    def _raise_already_exists(
            self,
            exc: Exception | None = None,
            message: str = "Object already exists",
            **context) -> None:
        self.logger.warning(
            message,
            **context,
        )
        if exc is None:
            raise AlreadyExistsException(message)
        raise AlreadyExistsException(message) from exc
