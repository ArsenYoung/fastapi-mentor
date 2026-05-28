from src.models.passports import PassportsOrm
from src.repositories.base import BaseRepository
from src.schemas.passports import Passport


class PassportsRepository(BaseRepository):
    model = PassportsOrm
    schema = Passport
