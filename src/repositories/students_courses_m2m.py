from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository
from src.schemas.students import Student


class StudentsCoursesRepository(BaseRepository):
    model = StudentsCoursesOrm
    schema = Student
