from src.db import get_session
from src.repositories.author import AuthorRepository
from src.repositories.book import BookRepository
from src.repositories.course import CourseRepository
from src.repositories.passport import PassportRepository
from src.repositories.person import PersonRepository
from src.repositories.student import StudentRepository
from src.repositories.students_courses import StudentsCoursesRepository
from src.services.author import AuthorService
from src.services.authors_books import AuthorsBooksService
from src.services.book import BookService
from src.services.course import CourseService
from src.services.passport import PassportService
from src.services.person import PersonService
from src.services.persons_passports import PersonsPassportsService
from src.services.student import StudentService
from src.services.students_courses import StudentsCoursesService


async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(
            AuthorService(AuthorRepository(session)),
            BookService(BookRepository(session)),
        )

async def get_persons_passports_service():
    async with get_session() as session:
        yield PersonsPassportsService(
            PersonService(PersonRepository(session)),
            PassportService(PassportRepository(session)),
        )

async def get_students_courses_service():
    async with get_session() as session:
        yield StudentsCoursesService(
            StudentsCoursesRepository(session),
            StudentService(StudentRepository(session)),
            CourseService(CourseRepository(session)),
        )
