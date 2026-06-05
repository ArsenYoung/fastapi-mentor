from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import Author
from src.schemas.books import Book


def build_author_response(author: AuthorsOrm, books: list[BooksOrm]) -> Author:
    return Author(
        id=author.id,
        author_code=author.author_code,
        first_name=author.first_name,
        last_name=author.last_name,
        books=[Book.model_validate(book) for book in books]
    )
