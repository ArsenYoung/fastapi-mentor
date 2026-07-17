import asyncio
from collections import Counter

import pytest

from conftest import TestSessionFactory, session_scope
from src.exceptions.base import AlreadyExistsException
from src.mappers.authors_books import AuthorsBooksMapper
from src.mappers.persons_passports import PersonsPassportsMapper
from src.mappers.students_courses import StudentCoursesMapper
from src.repositories.author import AuthorRepository
from src.repositories.person import PersonRepository
from src.repositories.student import StudentRepository
from src.schemas.authors import AuthorCreate, AuthorUpdate
from src.schemas.persons import PersonCreate, PersonUpdate
from src.schemas.students import StudentCreate, StudentUpdate
from src.services.authors_books import AuthorsBooksService
from src.services.persons_passports import PersonsPassportsService
from src.services.students_courses import StudentsCoursesService


def author_payload(
    *,
    author_code: str,
    book_code: str,
) -> dict:
    return {
        "author_code": author_code,
        "first_name": "Leo",
        "last_name": "Tolstoy",
        "books": [
            {
                "book_code": book_code,
                "title": "War and Peace",
            }
        ],
    }


def student_payload(
    *,
    record_book_number: str,
    reestr_number: str,
) -> dict:
    return {
        "first_name": "Alexey",
        "last_name": "Popov",
        "record_book_number": record_book_number,
        "courses": [
            {
                "reestr_number": reestr_number,
                "title": "Computer Science",
            }
        ],
    }


def person_payload(*, passport_number: str) -> dict:
    return {
        "first_name": "Alexey",
        "last_name": "Popov",
        "passport": {
            "number": passport_number,
            "registrated_in": "Moscow",
        },
    }


async def create_author_in_transaction(payload: dict):
    async with session_scope() as session:
        return await create_author_with_session(session, payload)


async def create_student_in_transaction(payload: dict):
    async with session_scope() as session:
        return await create_student_with_session(session, payload)


async def create_person_in_transaction(payload: dict):
    async with session_scope() as session:
        return await create_person_with_session(session, payload)


async def create_author_with_session(session, payload: dict):
    service = AuthorsBooksService(
        AuthorRepository(session),
        AuthorsBooksMapper(),
    )
    return await service.create(AuthorCreate.model_validate(payload))


async def create_student_with_session(session, payload: dict):
    service = StudentsCoursesService(
        StudentRepository(session),
        StudentCoursesMapper(),
    )
    return await service.create(StudentCreate.model_validate(payload))


async def create_person_with_session(session, payload: dict):
    service = PersonsPassportsService(
        PersonRepository(session),
        PersonsPassportsMapper(),
    )
    return await service.create(PersonCreate.model_validate(payload))


async def update_author_in_transaction(author_id: int, payload: dict):
    async with session_scope() as session:
        return await update_author_with_session(session, author_id, payload)


async def update_student_in_transaction(student_id: int, payload: dict):
    async with session_scope() as session:
        return await update_student_with_session(session, student_id, payload)


async def update_person_in_transaction(person_id: int, payload: dict):
    async with session_scope() as session:
        return await update_person_with_session(session, person_id, payload)


async def update_author_with_session(session, author_id: int, payload: dict):
    service = AuthorsBooksService(
        AuthorRepository(session),
        AuthorsBooksMapper(),
    )
    return await service.update(author_id, AuthorUpdate.model_validate(payload))


async def update_student_with_session(session, student_id: int, payload: dict):
    service = StudentsCoursesService(
        StudentRepository(session),
        StudentCoursesMapper(),
    )
    return await service.update(student_id, StudentUpdate.model_validate(payload))


async def update_person_with_session(session, person_id: int, payload: dict):
    service = PersonsPassportsService(
        PersonRepository(session),
        PersonsPassportsMapper(),
    )
    return await service.update(person_id, PersonUpdate.model_validate(payload))


async def capture_result(coroutine):
    try:
        return await coroutine
    except Exception as exc:
        return exc


async def run_against_uncommitted_create(
    create_with_session,
    create_in_transaction,
    first_payload: dict,
    second_payload: dict,
):
    async with TestSessionFactory() as session:
        first_result = await create_with_session(session, first_payload)
        second_task = asyncio.create_task(
            capture_result(create_in_transaction(second_payload))
        )

        await asyncio.sleep(0.1)
        assert second_task.done() is False
        await session.commit()

        second_result = await asyncio.wait_for(second_task, timeout=5)
        return [first_result, second_result]


async def run_against_uncommitted_update(
    update_with_session,
    update_in_transaction,
    first_id: int,
    second_id: int,
    first_payload: dict,
    second_payload: dict,
):
    async with TestSessionFactory() as session:
        first_result = await update_with_session(session, first_id, first_payload)
        second_task = asyncio.create_task(
            capture_result(update_in_transaction(second_id, second_payload))
        )

        await asyncio.sleep(0.1)
        assert second_task.done() is False
        await session.commit()

        second_result = await asyncio.wait_for(second_task, timeout=5)
        return [first_result, second_result]


def assert_result_counts(
    results,
    expected: dict[str, int],
    *,
    success_label: str = "created",
) -> None:
    unexpected_errors = [
        result
        for result in results
        if isinstance(result, BaseException)
        and not isinstance(result, AlreadyExistsException)
    ]
    assert unexpected_errors == []

    actual = Counter(
        "already_exists"
        if isinstance(result, AlreadyExistsException)
        else success_label
        for result in results
    )
    assert actual == expected


@pytest.mark.asyncio
async def test_concurrent_create_authors_with_same_author_code(client):
    results = await run_against_uncommitted_create(
        create_author_with_session,
        create_author_in_transaction,
        author_payload(author_code="A001", book_code="B001"),
        author_payload(author_code="A001", book_code="B002"),
    )

    assert_result_counts(results, {"created": 1, "already_exists": 1})

    list_response = await client.get("/authors")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["author_code"] == "A001"


@pytest.mark.asyncio
async def test_concurrent_create_authors_with_same_book_code(client):
    results = await run_against_uncommitted_create(
        create_author_with_session,
        create_author_in_transaction,
        author_payload(author_code="A001", book_code="B001"),
        author_payload(author_code="A002", book_code="B001"),
    )

    assert_result_counts(results, {"created": 1, "already_exists": 1})

    list_response = await client.get("/authors")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["books"][0]["book_code"] == "B001"


@pytest.mark.asyncio
async def test_concurrent_create_students_with_same_record_book_number(client):
    results = await run_against_uncommitted_create(
        create_student_with_session,
        create_student_in_transaction,
        student_payload(record_book_number="RB001", reestr_number="C001"),
        student_payload(record_book_number="RB001", reestr_number="C002"),
    )

    assert_result_counts(results, {"created": 1, "already_exists": 1})

    list_response = await client.get("/students")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["record_book_number"] == "RB001"


@pytest.mark.asyncio
async def test_concurrent_create_students_can_reuse_same_course(client):
    results = await run_against_uncommitted_create(
        create_student_with_session,
        create_student_in_transaction,
        student_payload(record_book_number="RB001", reestr_number="C001"),
        student_payload(record_book_number="RB002", reestr_number="C001"),
    )

    assert_result_counts(results, {"created": 2})

    list_response = await client.get("/students")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 2
    assert {item["record_book_number"] for item in body["items"]} == {
        "RB001",
        "RB002",
    }
    assert {item["courses"][0]["reestr_number"] for item in body["items"]} == {
        "C001",
    }


@pytest.mark.asyncio
async def test_concurrent_create_persons_with_same_passport_number(client):
    results = await run_against_uncommitted_create(
        create_person_with_session,
        create_person_in_transaction,
        person_payload(passport_number="P0001"),
        person_payload(passport_number="P0001"),
    )

    assert_result_counts(results, {"created": 1, "already_exists": 1})

    list_response = await client.get("/persons")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["passport"]["number"] == "P0001"


@pytest.mark.asyncio
async def test_concurrent_update_authors_to_same_author_code(client):
    first = await create_author_in_transaction(
        author_payload(author_code="A001", book_code="B001")
    )
    second = await create_author_in_transaction(
        author_payload(author_code="A002", book_code="B002")
    )

    results = await run_against_uncommitted_update(
        update_author_with_session,
        update_author_in_transaction,
        first.id,
        second.id,
        {"author_code": "A009"},
        {"author_code": "A009"},
    )

    assert_result_counts(
        results,
        {"updated": 1, "already_exists": 1},
        success_label="updated",
    )

    list_response = await client.get("/authors")
    assert list_response.status_code == 200
    body = list_response.json()
    assert Counter(item["author_code"] for item in body["items"]) == {
        "A009": 1,
        "A002": 1,
    }


@pytest.mark.asyncio
async def test_concurrent_update_students_to_same_record_book_number(client):
    first = await create_student_in_transaction(
        student_payload(record_book_number="RB001", reestr_number="C001")
    )
    second = await create_student_in_transaction(
        student_payload(record_book_number="RB002", reestr_number="C002")
    )

    results = await run_against_uncommitted_update(
        update_student_with_session,
        update_student_in_transaction,
        first.id,
        second.id,
        {"record_book_number": "RB009"},
        {"record_book_number": "RB009"},
    )

    assert_result_counts(
        results,
        {"updated": 1, "already_exists": 1},
        success_label="updated",
    )

    list_response = await client.get("/students")
    assert list_response.status_code == 200
    body = list_response.json()
    assert Counter(item["record_book_number"] for item in body["items"]) == {
        "RB009": 1,
        "RB002": 1,
    }


@pytest.mark.asyncio
async def test_concurrent_update_persons_to_same_passport_number(client):
    first = await create_person_in_transaction(person_payload(passport_number="P0001"))
    second = await create_person_in_transaction(person_payload(passport_number="P0002"))

    results = await run_against_uncommitted_update(
        update_person_with_session,
        update_person_in_transaction,
        first.id,
        second.id,
        {"passport": {"number": "P0009"}},
        {"passport": {"number": "P0009"}},
    )

    assert_result_counts(
        results,
        {"updated": 1, "already_exists": 1},
        success_label="updated",
    )

    list_response = await client.get("/persons")
    assert list_response.status_code == 200
    body = list_response.json()
    assert Counter(item["passport"]["number"] for item in body["items"]) == {
        "P0009": 1,
        "P0002": 1,
    }
