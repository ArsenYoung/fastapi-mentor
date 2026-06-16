from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.mappers.authors_books import map_book_payload_to_orm
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository):
    model = AuthorsOrm

    def _get_with_books_stmt(self):
        return (
            select(AuthorsOrm)
            .where(AuthorsOrm.is_deleted.is_(False))
            .options(
                joinedload(
                    AuthorsOrm.books.and_(BooksOrm.is_deleted.is_(False))
                )
            )
            .order_by(AuthorsOrm.id)
        )

    async def _get_author_with_books(self, author_id: int) -> AuthorsOrm | None:
        stmt = self._get_with_books_stmt().where(AuthorsOrm.id == author_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_author_by_code(self, author_code: str) -> AuthorsOrm | None:
        stmt = (
            select(AuthorsOrm)
            .where(
                AuthorsOrm.is_deleted.is_(False),
                AuthorsOrm.author_code == author_code,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_authors_by_book_codes(self, book_codes: list[str]) -> list[AuthorsOrm]:
        if not book_codes:
            return []
        stmt = (
            select(AuthorsOrm)
            .join(AuthorsOrm.books)
            .where(
                AuthorsOrm.is_deleted.is_(False),
                BooksOrm.is_deleted.is_(False),
                BooksOrm.book_code.in_(book_codes),
            )
            .options(
                joinedload(
                    AuthorsOrm.books.and_(BooksOrm.is_deleted.is_(False))
                )
            )
            .order_by(AuthorsOrm.id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def create_author_with_books(
        self,
        author_data: dict[str, str],
        books_data: list[dict[str, str]],
    ) -> AuthorsOrm:
        author = await self.create(**author_data)

        for book in books_data:
            self.session.add(map_book_payload_to_orm(author.id, book))
        await self.session.flush()
        created_author = await self._get_author_with_books(author.id)
        assert created_author is not None
        return created_author

    async def get_author_with_books(self, author_id: int) -> AuthorsOrm | None:
        return await self._get_author_with_books(author_id)

    async def get_authors_with_books_paginated_list(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[AuthorsOrm], bool]:
        stmt = self._get_with_books_stmt().offset(offset).limit(limit + 1)
        result = await self.session.execute(stmt)
        authors = list(result.unique().scalars().all())
        has_next = len(authors) > limit
        return authors[:limit], has_next
