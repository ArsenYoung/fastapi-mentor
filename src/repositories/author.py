from typing import Any, Sequence

from sqlalchemy import column, false, select, update, values
from sqlalchemy.dialects.postgresql import insert
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def create_author(
        self,
        author: AuthorsOrm,
    ) -> AuthorsOrm | None:
        stmt = (
            insert(AuthorsOrm)
            .values(**self._get_update_values(author))
            .on_conflict_do_nothing(
                index_elements=[AuthorsOrm.author_code],
                index_where=AuthorsOrm.is_deleted == false(),
            )
            .returning(AuthorsOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_author(
        self,
        author_id: int,
        update_values: dict[str, Any],
    ) -> AuthorsOrm | None:
        insert_stmt = insert(AuthorsOrm).values(
            id=author_id,
            author_code=update_values["author_code"],
            first_name=update_values["first_name"],
            last_name=update_values["last_name"],
            is_deleted=False,
        )

        stmt = (
            insert_stmt.on_conflict_do_update(
                index_elements=[AuthorsOrm.author_code],
                # если ставлю ON CONFLICT(author_code) не ловит конфликт по id и даёт IntegrityError.
                # если ставлю ON CONFLICT(id) обновит по id, но не ловит конфликт занятого author_code и тоже может дать IntegrityError.
                # Одним ON CONFLICT нельзя обработать оба случая как “id или author_code”.
                index_where=AuthorsOrm.is_deleted == false(),
                set_={
                    "id": insert_stmt.excluded.id,
                    "author_code": insert_stmt.excluded.author_code,
                    "first_name": insert_stmt.excluded.first_name,
                    "last_name": insert_stmt.excluded.last_name,
                }
            )
            .returning(AuthorsOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_books_by_author_id(
        self,
        author_id: int,
        books: Sequence[BooksOrm],
    ) -> list[str]:
        if not books:
            return []

        book_code_key = BooksOrm.book_code.key
        book_values = [self._get_update_values(book) for book in books]
        update_keys = [key for key in book_values[0] if key != book_code_key]

        if not update_keys:
            stmt = (
                select(BooksOrm.book_code)
                .where(
                    BooksOrm.author_id == author_id,
                    BooksOrm.book_code.in_(
                        [book_value[book_code_key] for book_value in book_values]
                    ),
                    BooksOrm.is_deleted.is_(False),
                )
                .order_by(BooksOrm.book_code)
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

        book_update_keys = [book_code_key, *update_keys]
        book_updates = (
            values(
                *[
                    column(key, getattr(BooksOrm, key).type)
                    for key in book_update_keys
                ],
                name="book_updates",
            )
            .data(
                [
                    tuple(book_value[key] for key in book_update_keys)
                    for book_value in book_values
                ]
            )
            .alias("book_updates")
        )
        stmt = (
            update(BooksOrm)
            .where(
                BooksOrm.author_id == author_id,
                BooksOrm.book_code == book_updates.c[book_code_key],
                BooksOrm.is_deleted.is_(False),
            )
            .values(
                {
                    key: book_updates.c[key]
                    for key in update_keys
                }
            )
            .returning(BooksOrm.book_code)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_books(
        self,
        books: Sequence[BooksOrm],
    ) -> list[BooksOrm]:
        if not books:
            return []

        stmt = (
            insert(BooksOrm)
            .values([self._get_update_values(book) for book in books])
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
