from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository
from src.schemas.persons import Person


class PersonsRepository(BaseRepository):
    model = PersonsOrm
    schema = Person
