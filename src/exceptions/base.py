class AppException(Exception):
    code = "unexpected_error"
    message = "Unexpected error"
    details = None

    def __init__(
        self,
        message: str | None = None,
        details: str | None = None,
    ):
        if message:
            self.message = message
        if details:
            self.details = details
        super().__init__(self.message)


class AlreadyExistsException(AppException):
    code = "already_exists_exception"
    message = "Object already exists"


class ObjectNotFoundException(AppException):
    code = "object_not_found_exception"
    message = "Object not found"
