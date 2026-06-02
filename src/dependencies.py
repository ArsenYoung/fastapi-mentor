from src.db import get_session
from src.repositories.persons_passports import PersonsPassportsRepository
from src.repositories.students_courses import StudentsCoursesRepository
from src.services.authors_books import AuthorsBooksService
from src.services.persons_passports import PersonsPassportsService
from src.services.students_courses import StudentsCoursesService


async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(session)

async def get_persons_passports_service():
    async with get_session() as session:
        yield PersonsPassportsService(PersonsPassportsRepository(session))

async def get_students_courses_service():
    async with get_session() as session:
        yield StudentsCoursesService(StudentsCoursesRepository(session))
