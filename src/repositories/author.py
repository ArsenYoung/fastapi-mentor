from typing import List, Sequence

from sqlalchemy import select

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def get_books_by_codes(self, book_codes: Sequence[str]) -> List[BooksOrm]:
        if not book_codes:
            return []
        stmt = select(BooksOrm).where(
            BooksOrm.is_deleted.is_(False),
            BooksOrm.book_code.in_(book_codes),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
