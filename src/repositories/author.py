from typing import Mapping, Sequence

from sqlalchemy import select

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def create_book(self, book: BooksOrm) -> BooksOrm:
        self.session.add(book)
        await self.session.flush()
        return book

    async def update_book(
        self,
        book: BooksOrm,
        values: Mapping[str, object],
    ) -> BooksOrm:
        for field, value in values.items():
            setattr(book, field, value)
        return book

    async def delete_book(self, book: BooksOrm) -> None:
        book.is_deleted = True

    async def get_books_by_codes(
        self,
        book_codes: Sequence[str],
    ) -> list[BooksOrm]:
        if not book_codes:
            return []

        stmt = select(BooksOrm).where(
            BooksOrm.is_deleted.is_(False),
            BooksOrm.book_code.in_(book_codes),
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
