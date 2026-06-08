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