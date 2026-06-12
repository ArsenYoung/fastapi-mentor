from sqlalchemy import select

from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class BookRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_id_active(self, book_id: int) -> BooksOrm | None:
        return await self.fetch_active_one(
            BooksOrm,
            id=book_id,
        )
    
    async def get_by_id_any(self, book_id: int) -> BooksOrm | None:
        return await self.fetch_one(
            select(BooksOrm)
            .filter_by(id=book_id)
        )
    
    async def get_by_code_active(self, book_code: str) -> BooksOrm | None:
        return await self.fetch_active_one(
            BooksOrm,
            book_code=book_code,
        )
    
    async def get_any_by_code(self, book_code: str) -> BooksOrm | None:
        stmt = (
            select(BooksOrm)
            .filter_by(book_code=book_code)
            .order_by(BooksOrm.id.desc())
        )
        return await self.fetch_one(stmt)
    
    async def get_by_author_id(self, author_id: int) -> list[BooksOrm]:
        return await self.fetch_active_all(
            BooksOrm,
            author_id=author_id,
        )
    
    async def get_by_author_ids(self, author_ids: list[int]) -> list[BooksOrm]:
        return await self.fetch_active_in(
            BooksOrm,
            BooksOrm.author_id,
            author_ids,
            order_by=BooksOrm.id,
        )
    
    async def insert(self, book_code: str, author_id: int, title: str) -> BooksOrm:
        return await self.insert_instance(
            BooksOrm(
                book_code=book_code,
                author_id=author_id,
                title=title,
            )
        )
    
    async def update(self, book_id: int, values: dict) -> None:
        await self.update_where(
            BooksOrm,
            values,
            id=book_id,
        )

    async def restore(self, book_id: int) -> None:
        await self.update_where(
            BooksOrm,
            {"is_deleted": False},
            id=book_id
        )

    async def soft_delete(self, book_id: int) -> None:
        await self.soft_delete_where(
            BooksOrm,
            id=book_id,
        )

    async def soft_delete_by_author(self, author_id: int) -> None:
        await self.soft_delete_where(
            BooksOrm,
            author_id=author_id,
        )
