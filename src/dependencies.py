from src.db import get_session
from src.repositories.authors_books import AuthorsBooksRepository
from src.repositories.course import CourseRepository
from src.repositories.persons_passports import PersonsPassportsRepository
from src.repositories.student import StudentRepository
from src.repositories.students_courses import StudentsCoursesRepository
from src.services.authors_books import AuthorsBooksService
from src.services.course import CourseService
from src.services.persons_passports import PersonsPassportsService
from src.services.student import StudentService
from src.services.students_courses import StudentsCoursesService


async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(AuthorsBooksRepository(session))

async def get_persons_passports_service():
    async with get_session() as session:
        yield PersonsPassportsService(PersonsPassportsRepository(session))

async def get_student_service():
    async with get_session() as session:
        yield StudentService(StudentRepository(session))

async def get_course_service():
    async with get_session() as session:
        yield CourseService(CourseRepository(session))

async def get_students_courses_service():
    async with get_session() as session:
        yield StudentsCoursesService(
            StudentsCoursesRepository(session),
            StudentService(StudentRepository(session)),
            CourseService(CourseRepository(session)),
        )
