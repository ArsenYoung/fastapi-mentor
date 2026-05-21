from src.models.books import BooksOrm
from src.repositories.base import BaseRepository
from src.schemas.books import Book


class BooksRepository(BaseRepository):
    model = BooksOrm
    schema = Book