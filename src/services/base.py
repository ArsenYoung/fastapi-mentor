from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from sqlalchemy.exc import IntegrityError
from typing import Mapping, Type
import structlog


class BaseService():
    logger = structlog.get_logger()

    def _raise_not_found(
            self,
            exception_cls: Type[ObjectNotFoundException] = ObjectNotFoundException,
            **context
    ) -> None:
        self.logger.warning(
            exception_cls.message,
            **context,
        )
        raise exception_cls()

    def _raise_already_exists(
            self,
            exception_cls: Type[AlreadyExistsException] = AlreadyExistsException,
            exc: Exception | None = None,
            **context) -> None:
        self.logger.warning(
            exception_cls.message,
            **context,
        )
        if exc is None:
            raise exception_cls()
        raise exception_cls() from exc

    def _raise_mapped_integrity_error(
            self,
            exc: IntegrityError,
            constraint_map: Mapping[str, Type[AlreadyExistsException]],
    ) -> None:
        error_text = str(exc)
        for constraint_name, exception_cls in constraint_map.items():
            if constraint_name in error_text:
                raise exception_cls() from exc
        raise exc
