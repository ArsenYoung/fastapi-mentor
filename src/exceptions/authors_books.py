from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException


class AuthorAlreadyExistsException(AlreadyExistsException):
    code = "author_already_exists_exception"
    message = "An author with this code already exists"


class BookAlreadyExistsException(AlreadyExistsException):
    code = "book_already_exists_exception"
    message = "A book with this code already exists"


class AuthorNotFoundException(ObjectNotFoundException):
    code = "author_not_found_exception"
    message = "Author not found"
