from src.models.students import StudentsOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentsOrm]):
    model = StudentsOrm
