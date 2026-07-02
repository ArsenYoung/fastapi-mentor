from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.schemas.errors import AuthorErrorDetails, BookErrorDetails


class AuthorNotFoundException(ObjectNotFoundException):
    message = "Author not found"

    def __init__(self, *, author_id: int):
        super().__init__(
            details=AuthorErrorDetails(author_id=author_id),
        )


class AuthorAlreadyExistsException(AlreadyExistsException):
    message = "An author with this code already exists"

    def __init__(self, *, author_code: str):
        super().__init__(
            details=AuthorErrorDetails(author_code=author_code),
        )


class BookAlreadyExistsException(AlreadyExistsException):
    message = "A book with this code already exists"

    def __init__(self, *, book_code: str):
        super().__init__(
            details=BookErrorDetails(book_code=book_code),
        )
