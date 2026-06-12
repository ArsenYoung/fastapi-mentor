from sqlalchemy.exc import IntegrityError

from src.models.books import BooksOrm
from src.repositories.book import BookRepository
from src.schemas.books import Book, BookCreateRequest, BookPatch
from src.services.base import BaseService


class BookService(BaseService):
    book_not_found_msg = "Book not found"
    book_already_exists_msg = "A book with this code already exists"
    book_unique_constraint = "uq_books_book_code_active"

    def __init__(self, repo: BookRepository):
        self.repo = repo

    def _is_book_unique_error(self, exc: IntegrityError) -> bool:
        return self.book_unique_constraint in str(exc)

    async def get_active_by_id_or_raise(self, book_id: int) -> BooksOrm:
        book = await self.repo.get_by_id_active(book_id)
        if book is None:
            self._raise_not_found(
                message=self.book_not_found_msg,
                book_id=book_id
            )
        return book
    
    async def get_any_by_code(self, book_code: str) -> BooksOrm | None:
        return await self.repo.get_any_by_code(book_code)

    async def get_by_author_id(self, author_id: int) -> list[Book]:
        books = await self.repo.get_by_author_id(author_id)
        return [Book.model_validate(book) for book in books]

    async def get_orm_by_author_id(self, author_id: int) -> list[BooksOrm]:
        return await self.repo.get_by_author_id(author_id)

    async def get_orm_by_author_ids(self, author_ids: list[int]) -> list[BooksOrm]:
        return await self.repo.get_by_author_ids(author_ids)
    
    async def create(self, author_id: int, data: BookCreateRequest) -> BooksOrm:
        try:
            return await self.repo.insert(
                author_id=author_id,
                book_code=data.book_code,
                title=data.title,
            )
        except IntegrityError as exc:
            if self._is_book_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.book_already_exists_msg,
                    book_code=data.book_code,
                )
            raise

    async def create_or_restore(self, author_id: int, data: BookCreateRequest) -> BooksOrm:
        book = await self.get_any_by_code(data.book_code)
        if book is None:
            return await self.create(author_id, data)
        if book.is_deleted:
            await self.restore(book.id)
            await self.update(
                book.id,
                BookPatch(
                    book_code=data.book_code,
                    title=data.title,
                )
            )
            return await self.get_active_by_id_or_raise(book.id)
        self._raise_already_exists(
            message=self.book_already_exists_msg,
            book_code=data.book_code,
        )

    async def update(self, book_id: int, data: BookPatch) -> None:
        await self.get_active_by_id_or_raise(book_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        if not values:
            return
        try:
            await self.repo.update(book_id, values)
        except IntegrityError as exc:
            if self._is_book_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.book_already_exists_msg,
                    book_id=book_id,
                    book_code=data.book_code,
                )
            raise

    async def soft_delete_by_author(self, author_id: int) -> None:
        await self.repo.soft_delete_by_author(author_id)

    async def soft_delete(self, book_id: int) -> None:
        await self.get_active_by_id_or_raise(book_id)
        await self.repo.soft_delete(book_id)

    async def restore(self, book_id: int) -> None:
        book = await self.repo.get_by_id_any(book_id)
        if book is None:
            self._raise_not_found(
               message=self.book_not_found_msg, 
               book_id=book_id
            )
        try:
            await self.repo.restore(book_id)
        except IntegrityError as exc:
            if self._is_book_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.book_already_exists_msg,
                    book_id=book_id,
                    book_code=book.book_code,
                )
            raise
