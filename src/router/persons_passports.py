from fastapi import APIRouter, Depends, Query, status

from src.dependencies import get_persons_passports_service
from src.schemas.common import CommonResponse
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.services.persons_passports import PersonsPassportsService

router = APIRouter(prefix="/persons", tags=["Persons and Passports 1-1"])


@router.post(
    "",
    response_model=Person,
    summary="Create a person with passport data",
    status_code=status.HTTP_201_CREATED,
)
async def create_person_with_passport(
    data: PersonCreate,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> Person:
    return await service.create(data)


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Get a person and their passport data",
    status_code=status.HTTP_200_OK,
)
async def get_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> Person:
    return await service.get(person_id)


@router.get(
    "",
    response_model=PersonsPaginatedList,
    summary="Get people and their passport data",
    status_code=status.HTTP_200_OK,
)
async def get_persons_with_passports_paginated_list(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> PersonsPaginatedList:
    return await service.get_paginated_list(limit, offset)


@router.delete(
    "/{person_id}",
    summary="Delete a person and their passport data",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> None:
    await service.delete(person_id)


@router.patch(
    "/{person_id}",
    response_model=CommonResponse,
    summary="Update person and passport data",
    status_code=status.HTTP_200_OK,
)
async def update_person_with_passport(
    person_id: int,
    data: PersonUpdate,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> CommonResponse:
    await service.update(person_id, data)
    return CommonResponse()
