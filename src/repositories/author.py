from typing import Sequence

from sqlalchemy import false, select
from sqlalchemy.dialects.postgresql import insert

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def insert_books_do_nothing(
        self,
        author_id: int,
        books: Sequence[tuple[str, str]],
    ) -> None:
        if not books:
            return

        stmt = (
            insert(BooksOrm)
            .values(
                [
                    {
                        "author_id": author_id,
                        "book_code": book_code,
                        "title": title,
                    }
                    for book_code, title in books
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[BooksOrm.book_code],
                index_where=BooksOrm.is_deleted == false(),
            )
        )
        await self.session.execute(stmt)

    async def get_books_by_codes(
        self,
        book_codes: Sequence[str],
        *,
        for_update: bool = False,
    ) -> list[BooksOrm]:
        stmt = (
            select(BooksOrm)
            .where(
                BooksOrm.is_deleted.is_(False),
                BooksOrm.book_code.in_(book_codes),
            )
            .order_by(BooksOrm.book_code)
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
