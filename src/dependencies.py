from src.db import get_session
from src.repositories.author import AuthorRepository
from src.repositories.person import PersonRepository
from src.repositories.student import StudentRepository
from src.services.authors_books import AuthorsBooksService
from src.services.persons_passports import PersonsPassportsService
from src.services.students_courses import StudentsCoursesService


async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(AuthorRepository(session))

async def get_persons_passports_service():
    async with get_session() as session:
        yield PersonsPassportsService(PersonRepository(session))

async def get_students_courses_service():
    async with get_session() as session:
        yield StudentsCoursesService(StudentRepository(session))
