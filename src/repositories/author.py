from pickletools import int4
from typing import Any, Sequence

from sqlalchemy import false, select
from sqlalchemy.dialects.postgresql import insert

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def create_do_nothing(
        self,
        values: dict[str, Any],
    ) -> int | None:
        stmt = (
            insert(AuthorsOrm)
            .values(values)
            .on_conflict_do_nothing(
                index_elements=[AuthorsOrm.author_code],
                index_where=AuthorsOrm.is_deleted == false(),
            )
            .returning(AuthorsOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_books_do_nothing(
        self,
        values: Sequence[dict[str, Any]],
    ) -> None:
        if not values:
            return

        stmt = (
            insert(BooksOrm)
            .values(list(values))
            .on_conflict_do_nothing(
                index_elements=[BooksOrm.book_code],
                index_where=BooksOrm.is_deleted == false(),
            )
        )
        await self.session.execute(stmt)

    async def get_books_by_codes(
        self,
        book_codes: Sequence[str],
    ) -> list[BooksOrm]:
        stmt = (
            select(BooksOrm)
            .where(
                BooksOrm.is_deleted.is_(False),
                BooksOrm.book_code.in_(book_codes),
            )
            .order_by(BooksOrm.book_code)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
