from contextlib import asynccontextmanager

import httpx
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.application import get_app
from src.config import Settings
from src.dependencies import (
    get_authors_books_service,
    get_persons_passports_service,
    get_students_courses_service,
)
from src.mappers.authors_books import AuthorsBooksMapper
from src.mappers.persons_passports import PersonsPassportsMapper
from src.mappers.students_courses import StudentCoursesMapper
from src.repositories.author import AuthorRepository
from src.repositories.person import PersonRepository
from src.repositories.student import StudentRepository
from src.services.authors_books import AuthorsBooksService
from src.services.persons_passports import PersonsPassportsService
from src.services.students_courses import StudentsCoursesService


test_engine = create_async_engine(
    str(Settings().postgres_url),
    poolclass=NullPool,
)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

TRUNCATE_SQL = text(
    """
    TRUNCATE TABLE
        students_courses,
        books,
        passports,
        authors,
        courses,
        students,
        persons
    RESTART IDENTITY CASCADE
    """
)


@asynccontextmanager
async def session_scope():
    async with TestSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_authors_books_service():
    async with session_scope() as session:
        yield AuthorsBooksService(
            AuthorRepository(session),
            AuthorsBooksMapper(),
        )


async def override_students_courses_service():
    async with session_scope() as session:
        yield StudentsCoursesService(
            StudentRepository(session),
            StudentCoursesMapper(),
        )


async def override_persons_passports_service():
    async with session_scope() as session:
        yield PersonsPassportsService(
            PersonRepository(session),
            PersonsPassportsMapper(),
        )


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with TestSessionFactory() as session:
        await session.execute(TRUNCATE_SQL)
        await session.commit()


@pytest_asyncio.fixture
async def client():
    app = get_app()
    app.dependency_overrides[get_authors_books_service] = (
        override_authors_books_service
    )
    app.dependency_overrides[get_students_courses_service] = (
        override_students_courses_service
    )
    app.dependency_overrides[get_persons_passports_service] = (
        override_persons_passports_service
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
