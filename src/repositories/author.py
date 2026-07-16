from typing import Sequence

from sqlalchemy import false, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def create_do_nothing(
        self,
        author: AuthorsOrm,
    ) -> AuthorsOrm | None:
        stmt = (
            insert(AuthorsOrm)
            .values(
                author_code=author.author_code,
                first_name=author.first_name,
                last_name=author.last_name,
            )
            .on_conflict_do_nothing(
                index_elements=[AuthorsOrm.author_code],
                index_where=AuthorsOrm.is_deleted == false(),
            )
            .returning(AuthorsOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(
        self,
        item_id: int,
        patch: AuthorsOrm,
    ) -> AuthorsOrm | None:
        values = self._get_update_values(patch)
        if not values:
            return await self.get(id=item_id)

        stmt = (
            update(AuthorsOrm)
            .where(
                AuthorsOrm.id == item_id,
                AuthorsOrm.is_deleted.is_(False),
            )
            .values(**values)
            .returning(AuthorsOrm)
        )

        if "author_code" in values:
            other_author = aliased(AuthorsOrm)
            stmt = stmt.where(
                ~select(other_author.id)
                .where(
                    other_author.author_code == values["author_code"],
                    other_author.is_deleted.is_(False),
                    other_author.id != item_id,
                )
                .exists()
            )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_book_by_id(
        self,
        book_id: int,
        patch: BooksOrm,
    ) -> BooksOrm | None:
        values = self._get_update_values(patch)
        if not values:
            stmt = select(BooksOrm).where(
                BooksOrm.id == book_id,
                BooksOrm.is_deleted.is_(False),
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        stmt = (
            update(BooksOrm)
            .where(
                BooksOrm.id == book_id,
                BooksOrm.is_deleted.is_(False),
            )
            .values(**values)
            .returning(BooksOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_books_do_nothing(
        self,
        books: Sequence[BooksOrm],
    ) -> list[BooksOrm]:
        if not books:
            return []

        stmt = (
            insert(BooksOrm)
            .values(
                [
                    {
                        "author_id": book.author_id,
                        "book_code": book.book_code,
                        "title": book.title,
                    }
                    for book in books
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[BooksOrm.book_code],
                index_where=BooksOrm.is_deleted == false(),
            )
            .returning(BooksOrm)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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

    async def get_books_by_author_id(
        self,
        author_id: int,
        *,
        for_update: bool = False,
    ) -> list[BooksOrm]:
        stmt = (
            select(BooksOrm)
            .where(
                BooksOrm.is_deleted.is_(False),
                BooksOrm.author_id == author_id,
            )
            .order_by(BooksOrm.id)
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
