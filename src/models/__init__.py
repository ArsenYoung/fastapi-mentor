"""Package initializer for src.models."""

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.models.persons import PersonsOrm
from src.models.passports import PassportsOrm

__all__ = ["AuthorsOrm", "BooksOrm", "CoursesOrm", "StudentsOrm", "StudentsCoursesOrm", "PersonsOrm", "PassportsOrm"]
