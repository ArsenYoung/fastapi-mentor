from collections.abc import Iterable

from sqlalchemy import select

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorsBooksRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_author(self, author_id: int) -> AuthorsOrm | None:
        return await self.fetch_active_one(AuthorsOrm, id=author_id)

    async def get_author_by_code(self, author_code: str) -> AuthorsOrm | None:
        stmt = (
            select(AuthorsOrm)
            .filter_by(author_code=author_code)
            .order_by(AuthorsOrm.id.desc())
        )
        return await self.fetch_one(stmt)

    async def get_authors_page(self, limit: int, offset: int) -> tuple[list[AuthorsOrm], int]:
        return await self.fetch_active_page(
            AuthorsOrm,
            limit=limit,
            offset=offset,
            order_by=AuthorsOrm.id,
        )

    async def get_books_by_author(self, author_id: int) -> list[BooksOrm]:
        return await self.fetch_active_all(
            BooksOrm,
            author_id=author_id,
        )

    async def get_books_by_author_ids(self, author_ids: Iterable[int]) -> list[BooksOrm]:
        return await self.fetch_active_in(
            BooksOrm,
            BooksOrm.author_id,
            author_ids,
            order_by=BooksOrm.id,
        )

    async def get_book(self, book_code: str, author_id: int) -> BooksOrm | None:
        return await self.fetch_active_one(
            BooksOrm,
            book_code=book_code,
            author_id=author_id,
        )

    async def insert_author(self, author_code: str, first_name: str, last_name: str) -> AuthorsOrm:
        return await self.insert_instance(
            AuthorsOrm(
                author_code=author_code,
                first_name=first_name,
                last_name=last_name,
            )
        )

    async def insert_book(self, author_id: int, book_code: str, title: str) -> BooksOrm:
        return await self.insert_instance(
            BooksOrm(
                author_id=author_id,
                book_code=book_code,
                title=title,
            )
        )

    async def update_author(self, author_id: int, values: dict) -> None:
        await self.update_where(
            AuthorsOrm,
            values,
            id=author_id,
        )

    async def update_book(self, book_code: str, author_id: int, values: dict) -> None:
        await self.update_where(
            BooksOrm,
            values,
            book_code=book_code,
            author_id=author_id,
        )

    async def restore_author(self, author_id: int) -> None:
        await self.update_where(
            AuthorsOrm,
            {"is_deleted": False},
            id=author_id,
        )

    async def soft_delete_author(self, author_id: int) -> None:
        await self.soft_delete_where(
            AuthorsOrm,
            id=author_id,
        )

    async def soft_delete_books_by_author(self, author_id: int) -> None:
        await self.soft_delete_where(
            BooksOrm,
            author_id=author_id,
        )
