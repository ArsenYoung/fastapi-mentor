from src.models.authors import AuthorsOrm
from src.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsOrm]):
    model = AuthorsOrm
