from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class BookRepository(BaseRepository):
    model = BooksOrm

    def __init__(self, session):
        self.session = session
    
    async def get_any_by_code(self, book_code: str) -> BooksOrm | None:
        return await self.get_latest_one(
            BooksOrm,
            BooksOrm.id,
            book_code=book_code,
        )
    
    async def get_by_author_id(self, author_id: int) -> list[BooksOrm]:
        return await self.get_many_active(
            BooksOrm,
            author_id=author_id,
        )
    
    async def get_by_author_ids(self, author_ids: list[int]) -> list[BooksOrm]:
        return await self.get_many_active_in(
            BooksOrm,
            BooksOrm.author_id,
            author_ids,
            order_by=BooksOrm.id,
        )
    
    async def insert(self, book_code: str, author_id: int, title: str) -> BooksOrm:
        return await self.insert_model(
            book_code=book_code,
            author_id=author_id,
            title=title,
        )

    async def soft_delete_by_author(self, author_id: int) -> None:
        await self.soft_delete_where(
            BooksOrm,
            author_id=author_id,
        )
