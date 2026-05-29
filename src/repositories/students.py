from src.models.students import StudentsOrm
from src.repositories.base import BaseRepository
from src.schemas.students import Student


class StudentsRepository(BaseRepository):
    model = StudentsOrm
    schema = Student
