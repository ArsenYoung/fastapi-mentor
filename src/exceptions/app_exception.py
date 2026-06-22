from typing import Dict, List


class AppException(Exception):
    message = "Unexpected error"
    details = None

    def __init__(
        self,
        *,
        message: str | None = None,
        details: Dict | List | str | None = None,
    ):
        if message is not None:
            self.message = message
        if details is not None:
            self.details = details
        super().__init__(self.message)
