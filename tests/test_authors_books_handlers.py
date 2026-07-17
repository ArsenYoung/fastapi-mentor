import pytest


def author_payload(
    author_code: str = "A001",
    book_code: str = "B001",
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


async def create_author(
    client,
    author_code: str = "A001",
    book_code: str = "B001",
) -> dict:
    response = await client.post(
        "/authors",
        json=author_payload(author_code, book_code),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_create_author_with_books(client):
    author = await create_author(client)

    assert author["id"] == 1
    assert author["author_code"] == "A001"
    assert author["first_name"] == "Leo"
    assert author["last_name"] == "Tolstoy"
    assert author["books"] == [
        {
            "id": 1,
            "book_code": "B001",
            "title": "War and Peace",
        }
    ]


@pytest.mark.asyncio
async def test_create_author_duplicate_author_code_returns_409(client):
    await create_author(client, author_code="A001", book_code="B001")

    response = await client.post(
        "/authors",
        json=author_payload(author_code="A001", book_code="B002"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"author_code": "A001"}


@pytest.mark.asyncio
async def test_create_author_duplicate_book_code_returns_409(client):
    await create_author(client, author_code="A001", book_code="B001")

    response = await client.post(
        "/authors",
        json=author_payload(author_code="A002", book_code="B001"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"book_code": "B001"}


@pytest.mark.asyncio
async def test_get_author_with_books(client):
    created = await create_author(client)

    response = await client.get(f"/authors/{created['id']}")

    assert response.status_code == 200
    assert response.json()["author_code"] == "A001"


@pytest.mark.asyncio
async def test_get_missing_author_returns_404(client):
    response = await client.get("/authors/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"author_id": 999}


@pytest.mark.asyncio
async def test_list_authors_pagination(client):
    await create_author(client, author_code="A001", book_code="B001")
    await create_author(client, author_code="A002", book_code="B002")

    response = await client.get("/authors", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["has_next"] is True
    assert body["limit"] == 1
    assert body["offset"] == 0


@pytest.mark.asyncio
async def test_delete_author_with_books(client):
    created = await create_author(client)

    delete_response = await client.delete(f"/authors/{created['id']}")
    get_response = await client.get(f"/authors/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_author_returns_404(client):
    response = await client.delete("/authors/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"author_id": 999}


@pytest.mark.asyncio
async def test_patch_author_and_book(client):
    created = await create_author(client)

    response = await client.patch(
        f"/authors/{created['id']}",
        json={
            "author_code": "A009",
            "first_name": "Lev",
            "books": [
                {
                    "book_code": "B001",
                    "title": "Anna Karenina",
                }
            ],
        },
    )
    updated_response = await client.get(f"/authors/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    updated = updated_response.json()
    assert updated["author_code"] == "A009"
    assert updated["first_name"] == "Lev"
    assert updated["last_name"] == "Tolstoy"
    assert updated["books"][0]["title"] == "Anna Karenina"


@pytest.mark.asyncio
async def test_patch_author_duplicate_author_code_returns_409(client):
    await create_author(client, author_code="A001", book_code="B001")
    second = await create_author(client, author_code="A002", book_code="B002")

    response = await client.patch(
        f"/authors/{second['id']}",
        json={"author_code": "A001"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"author_code": "A001"}


@pytest.mark.asyncio
async def test_patch_missing_author_returns_404(client):
    response = await client.patch("/authors/999", json={"first_name": "Lev"})

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"author_id": 999}


@pytest.mark.asyncio
async def test_patch_author_missing_book_returns_404(client):
    created = await create_author(client)

    response = await client.patch(
        f"/authors/{created['id']}",
        json={
            "books": [
                {
                    "book_code": "B999",
                    "title": "Missing",
                }
            ]
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"book_code": "B999"}


@pytest.mark.asyncio
async def test_patch_author_book_owned_by_another_author_returns_409(client):
    first = await create_author(client, author_code="A001", book_code="B001")
    await create_author(client, author_code="A002", book_code="B002")

    response = await client.patch(
        f"/authors/{first['id']}",
        json={
            "books": [
                {
                    "book_code": "B002",
                    "title": "Foreign Book",
                }
            ]
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"book_code": "B002"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"author_code": "A001", "first_name": "Leo", "last_name": "Tolstoy", "books": []},
        {"author_code": "", "first_name": "Leo", "last_name": "Tolstoy", "books": []},
    ],
)
async def test_create_author_validation_errors(client, payload):
    response = await client.post("/authors", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_authors_validation_error(client):
    response = await client.get("/authors", params={"limit": 0})

    assert response.status_code == 422
