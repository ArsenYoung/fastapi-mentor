from src.exceptions.base import NotFoundError


class BookNotFoundError(NotFoundError):
    code = "book_not_found_error"
    message = "Книга не найдена"