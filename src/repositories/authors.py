from src.models.authors import AuthorsOrm
from src.repositories.base import BaseRepository
from src.schemas.authors import Author


class AuthorsRepository(BaseRepository):
    model = AuthorsOrm
    schema = Author