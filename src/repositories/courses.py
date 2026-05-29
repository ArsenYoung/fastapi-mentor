from src.models.courses import CoursesOrm
from src.repositories.base import BaseRepository
from src.schemas.courses import Course


class CoursesRepository(BaseRepository):
    model = CoursesOrm
    schema = Course
