from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm

    async def get_authors_by_book_codes(
        self, book_codes: Sequence[str]
    ) -> List[AuthorsOrm]:
        if not book_codes:
            return []
        stmt = (
            select(AuthorsOrm)
            .join(AuthorsOrm.books)
            .where(
                BooksOrm.book_code.in_(book_codes),
            )
            .options(joinedload(AuthorsOrm.books))
            .execution_options(populate_existing=True)
            .order_by(AuthorsOrm.id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
