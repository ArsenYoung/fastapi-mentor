from src.models.authors import AuthorsOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository):
    model = AuthorsOrm

    def __init__(self, session):
        self.session = session
    
    async def get_any_by_author_code(self, author_code: str) -> AuthorsOrm | None:
        return await self.get_latest_one(
            AuthorsOrm,
            AuthorsOrm.id,
            author_code=author_code,
        )
    
    async def insert(
        self,
        author_code: str,
        first_name: str,
        last_name: str,
    ) -> AuthorsOrm:
        return await self.insert_model(
            author_code=author_code,
            first_name=first_name,
            last_name=last_name,
        )
