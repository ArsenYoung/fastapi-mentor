from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository
from src.schemas.authors import AuthorBookUpdateRequest, AuthorCreate, AuthorUpdate


class AuthorRepository(BaseRepository):
    model = AuthorsOrm

    def __init__(self, session):
        self.session = session

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

    async def _get_author_with_books_or_none(self, author_id: int) -> AuthorsOrm | None:
        stmt = self._get_with_books_stmt().where(AuthorsOrm.id == author_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_author_code(self, author_code: str) -> AuthorsOrm | None:
        return await self.get_one(
            AuthorsOrm,
            author_code=author_code,
        )

    async def get_books_by_codes(self, book_codes: list[str]) -> list[BooksOrm]:
        return await self.get_many_in(
            BooksOrm,
            BooksOrm.book_code,
            book_codes,
            order_by=BooksOrm.id,
        )

    async def create_author_with_books(self, data: AuthorCreate) -> AuthorsOrm:
        author = await self.insert(
            author_code=data.author_code,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        for book in data.books:
            self.session.add(
                BooksOrm(
                    author_id=author.id,
                    book_code=book.book_code,
                    title=book.title,
                )
            )
        await self.session.flush()
        created_author = await self._get_author_with_books_or_none(author.id)
        assert created_author is not None
        return created_author

    async def get_author_with_books(self, author_id: int) -> AuthorsOrm | None:
        return await self._get_author_with_books_or_none(author_id)

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

    async def delete_author_with_books(self, author_id: int) -> AuthorsOrm | None:
        author = await self._get_author_with_books_or_none(author_id)
        if author is None:
            return None
        await self.session.execute(
            update(BooksOrm)
            .filter_by(author_id=author_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )
        await self.soft_delete(author_id)
        return author

    async def _sync_books(self, author_id: int, books_data: list[AuthorBookUpdateRequest]) -> None:
        author = await self._get_author_with_books_or_none(author_id)
        if author is None:
            return
        existing_books_by_code = {book.book_code: book for book in author.books}

        target_codes: set[str] = set()
        for item in books_data:
            target_codes.add(item.book_code)
            existing_book = existing_books_by_code.get(item.book_code)
            if existing_book is not None:
                if existing_book.title != item.title:
                    await self.update_book(existing_book.id, {"title": item.title})
                continue

            self.session.add(
                BooksOrm(
                    author_id=author_id,
                    book_code=item.book_code,
                    title=item.title,
                )
            )

        for book in author.books:
            if book.book_code not in target_codes:
                await self.update_book(book.id, {"is_deleted": True})

        await self.session.flush()

    async def update_book(self, book_id: int, values: dict) -> None:
        await self.session.execute(
            update(BooksOrm)
            .filter_by(id=book_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def update_author_with_books(self, author_id: int, data: AuthorUpdate) -> AuthorsOrm:
        author = await self._get_author_with_books_or_none(author_id)
        if author is None:
            return None

        author_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"books"},
        )
        if author_data:
            await self.update(author_id, author_data)

        if data.books is not None:
            await self._sync_books(author_id, data.books)

        return await self._get_author_with_books_or_none(author_id)
