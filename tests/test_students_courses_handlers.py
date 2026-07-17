import pytest


def student_payload(
    record_book_number: str = "RB001",
    reestr_number: str = "C001",
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


async def create_student(
    client,
    record_book_number: str = "RB001",
    reestr_number: str = "C001",
) -> dict:
    response = await client.post(
        "/students",
        json=student_payload(record_book_number, reestr_number),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_create_student_with_courses(client):
    student = await create_student(client)

    assert student["id"] == 1
    assert student["record_book_number"] == "RB001"
    assert student["first_name"] == "Alexey"
    assert student["last_name"] == "Popov"
    assert student["courses"] == [
        {
            "id": 1,
            "reestr_number": "C001",
            "title": "Computer Science",
        }
    ]


@pytest.mark.asyncio
async def test_create_student_duplicate_record_book_number_returns_409(client):
    await create_student(client, record_book_number="RB001", reestr_number="C001")

    response = await client.post(
        "/students",
        json=student_payload(record_book_number="RB001", reestr_number="C002"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"record_book_number": "RB001"}


@pytest.mark.asyncio
async def test_create_second_student_can_reuse_existing_course(client):
    await create_student(client, record_book_number="RB001", reestr_number="C001")

    second = await create_student(
        client,
        record_book_number="RB002",
        reestr_number="C001",
    )

    assert second["record_book_number"] == "RB002"
    assert second["courses"][0]["reestr_number"] == "C001"


@pytest.mark.asyncio
async def test_get_student_with_courses(client):
    created = await create_student(client)

    response = await client.get(f"/students/{created['id']}")

    assert response.status_code == 200
    assert response.json()["record_book_number"] == "RB001"


@pytest.mark.asyncio
async def test_get_missing_student_returns_404(client):
    response = await client.get("/students/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"student_id": 999}


@pytest.mark.asyncio
async def test_list_students_pagination(client):
    await create_student(client, record_book_number="RB001", reestr_number="C001")
    await create_student(client, record_book_number="RB002", reestr_number="C002")

    response = await client.get("/students", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["has_next"] is True
    assert body["limit"] == 1
    assert body["offset"] == 0


@pytest.mark.asyncio
async def test_delete_student_with_courses(client):
    created = await create_student(client)

    delete_response = await client.delete(f"/students/{created['id']}")
    get_response = await client.get(f"/students/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_student_returns_404(client):
    response = await client.delete("/students/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"student_id": 999}


@pytest.mark.asyncio
async def test_patch_student_and_courses(client):
    created = await create_student(client)

    response = await client.patch(
        f"/students/{created['id']}",
        json={
            "first_name": "Alex",
            "record_book_number": "RB009",
            "courses": [
                {
                    "reestr_number": "C001",
                    "title": "Algorithms",
                },
                {
                    "reestr_number": "C002",
                    "title": "Databases",
                },
            ],
        },
    )
    updated_response = await client.get(f"/students/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    updated = updated_response.json()
    assert updated["first_name"] == "Alex"
    assert updated["record_book_number"] == "RB009"
    assert [course["reestr_number"] for course in updated["courses"]] == [
        "C001",
        "C002",
    ]
    assert [course["title"] for course in updated["courses"]] == [
        "Algorithms",
        "Databases",
    ]


@pytest.mark.asyncio
async def test_patch_student_duplicate_record_book_number_returns_409(client):
    await create_student(client, record_book_number="RB001", reestr_number="C001")
    second = await create_student(
        client,
        record_book_number="RB002",
        reestr_number="C002",
    )

    response = await client.patch(
        f"/students/{second['id']}",
        json={"record_book_number": "RB001"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"record_book_number": "RB001"}


@pytest.mark.asyncio
async def test_patch_missing_student_returns_404(client):
    response = await client.patch("/students/999", json={"first_name": "Alex"})

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"student_id": 999}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "record_book_number": "RB001",
            "courses": [],
        },
        {
            "first_name": "",
            "last_name": "Popov",
            "record_book_number": "RB001",
            "courses": [{"reestr_number": "C001", "title": "Computer Science"}],
        },
    ],
)
async def test_create_student_validation_errors(client, payload):
    response = await client.post("/students", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_validation_error(client):
    response = await client.get("/students", params={"offset": -1})

    assert response.status_code == 422
