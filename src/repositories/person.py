from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository[PersonsOrm]):
    model = PersonsOrm
