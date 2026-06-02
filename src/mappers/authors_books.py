from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import Author
from src.schemas.books import Book


def build_author_response(author: AuthorsOrm, books: list[BooksOrm]) -> Author:
    return Author(
        id=author.id,
        name=author.name,
        books=[Book.model_validate(book) for book in books]
    )
