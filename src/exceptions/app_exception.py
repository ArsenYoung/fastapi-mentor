from src.schemas.errors import ErrorDetailsType


class AppException(Exception):
    message = "Unexpected error"
    details = None

    def __init__(
        self,
        *,
        message: str | None = None,
        details: ErrorDetailsType = None,
    ):
        if message is not None:
            self.message = message
        if details is not None:
            self.details = details
        super().__init__(self.message)
