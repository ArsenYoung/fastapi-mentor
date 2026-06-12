from sqlalchemy import select

from src.models.authors import AuthorsOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository):
    def __init__(self, session):
       self.session = session

    async def get_by_id_active(self, author_id: int) -> AuthorsOrm | None:
        return await self.fetch_active_one(
            AuthorsOrm,
            id=author_id,
        )
    
    async def get_by_id_any(self, author_id: int) -> AuthorsOrm | None:
        return await self.fetch_one(
            select(AuthorsOrm)
            .filter_by(id=author_id)
        )
    
    async def get_any_by_author_code(self, author_code: str) -> AuthorsOrm | None:
        stmt = (
            select(AuthorsOrm)
            .filter_by(author_code=author_code)
            .order_by(AuthorsOrm.id.desc())
        )
        return await self.fetch_one(stmt)

    async def get_page(self, limit: int, offset: int) -> tuple[list[AuthorsOrm], int]:
        return await self.fetch_active_page(
            AuthorsOrm,
            limit=limit,
            offset=offset,
            order_by=AuthorsOrm.id
        )
    
    async def insert(
            self, 
            author_code: str,
            first_name: str,
            last_name: str,
    ) -> AuthorsOrm:
        return await self.insert_instance(
            AuthorsOrm(
                author_code=author_code,
                first_name=first_name,
                last_name=last_name,
            )
        )
    
    async def update(self, author_id: int, values: dict) -> None:
        await self.update_where(
            AuthorsOrm,
            values,
            id=author_id,
        )
    
    async def soft_delete(self, author_id: int) -> None:
        await self.soft_delete_where(
            AuthorsOrm,
            id=author_id,
        )

    async def restore(self, author_id: int) -> None:
        await self.update_where(
            AuthorsOrm,
            {"is_deleted": False},
            id=author_id
        )
        
