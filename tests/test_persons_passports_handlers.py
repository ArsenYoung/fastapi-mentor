import pytest


def person_payload(passport_number: str = "P0001") -> dict:
    return {
        "first_name": "Alexey",
        "last_name": "Popov",
        "passport": {
            "number": passport_number,
            "registrated_in": "Moscow",
        },
    }


async def create_person(client, passport_number: str = "P0001") -> dict:
    response = await client.post(
        "/persons",
        json=person_payload(passport_number),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_create_person_with_passport(client):
    person = await create_person(client)

    assert person["id"] == 1
    assert person["first_name"] == "Alexey"
    assert person["last_name"] == "Popov"
    assert person["passport"] == {
        "id": 1,
        "number": "P0001",
        "registrated_in": "Moscow",
    }


@pytest.mark.asyncio
async def test_create_person_duplicate_passport_number_returns_409(client):
    await create_person(client, passport_number="P0001")

    response = await client.post(
        "/persons",
        json=person_payload(passport_number="P0001"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"passport_number": "P0001"}


@pytest.mark.asyncio
async def test_get_person_with_passport(client):
    created = await create_person(client)

    response = await client.get(f"/persons/{created['id']}")

    assert response.status_code == 200
    assert response.json()["passport"]["number"] == "P0001"


@pytest.mark.asyncio
async def test_get_missing_person_returns_404(client):
    response = await client.get("/persons/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"person_id": 999}


@pytest.mark.asyncio
async def test_list_persons_pagination(client):
    await create_person(client, passport_number="P0001")
    await create_person(client, passport_number="P0002")

    response = await client.get("/persons", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["has_next"] is True
    assert body["limit"] == 1
    assert body["offset"] == 0


@pytest.mark.asyncio
async def test_delete_person_with_passport(client):
    created = await create_person(client)

    delete_response = await client.delete(f"/persons/{created['id']}")
    get_response = await client.get(f"/persons/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_person_returns_404(client):
    response = await client.delete("/persons/999")

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"person_id": 999}


@pytest.mark.asyncio
async def test_patch_person_and_passport(client):
    created = await create_person(client)

    response = await client.patch(
        f"/persons/{created['id']}",
        json={
            "first_name": "Alex",
            "passport": {
                "number": "P0099",
                "registrated_in": "Tbilisi",
            },
        },
    )
    updated_response = await client.get(f"/persons/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    updated = updated_response.json()
    assert updated["first_name"] == "Alex"
    assert updated["last_name"] == "Popov"
    assert updated["passport"]["number"] == "P0099"
    assert updated["passport"]["registrated_in"] == "Tbilisi"


@pytest.mark.asyncio
async def test_patch_person_duplicate_passport_number_returns_409(client):
    await create_person(client, passport_number="P0001")
    second = await create_person(client, passport_number="P0002")

    response = await client.patch(
        f"/persons/{second['id']}",
        json={"passport": {"number": "P0001"}},
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"] == {"passport_number": "P0001"}


@pytest.mark.asyncio
async def test_patch_missing_person_returns_404(client):
    response = await client.patch("/persons/999", json={"first_name": "Alex"})

    assert response.status_code == 404
    assert response.json()["error"]["details"] == {"person_id": 999}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "first_name": "",
            "last_name": "Popov",
            "passport": {"number": "P0001", "registrated_in": "Moscow"},
        },
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "passport": {"number": "", "registrated_in": "Moscow"},
        },
    ],
)
async def test_create_person_validation_errors(client, payload):
    response = await client.post("/persons", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_persons_validation_error(client):
    response = await client.get("/persons", params={"limit": 101})

    assert response.status_code == 422
