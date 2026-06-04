from fastapi import APIRouter, Depends, Query, status

from src.dependencies import get_persons_passports_service
from src.schemas.common import CommonResponse
from src.schemas.persons import PersonAddRequest, PersonPage, PersonPatch, PersonRead
from src.services.persons_passports import PersonsPassportsService


router = APIRouter(prefix="/persons", tags=["People and Passports 1-1"])


@router.post("", summary="Create a person with passport data", status_code=status.HTTP_201_CREATED)
async def post_person_with_passport(
    data: PersonAddRequest,
    service: PersonsPassportsService = Depends(get_persons_passports_service)
) -> CommonResponse:
    await service.create_person_with_passport(data)
    return CommonResponse

@router.get("/{person_id}", response_model=PersonRead, summary="Get a person and their passport data", status_code=status.HTTP_200_OK)
async def get_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> PersonRead:
    return await service.get_person_with_passport(person_id)

@router.get("", response_model=PersonPage, summary="Get people and their passport data", status_code=status.HTTP_200_OK)
async def get_all_persons_with_passports(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> PersonPage:
    return await service.get_all_persons_with_passports(limit, offset)

@router.delete("/{person_id}", summary="Delete a person and their passport data", status_code=status.HTTP_204_NO_CONTENT)
async def del_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> None:
    await service.del_person_with_passport(person_id)

@router.patch("/{person_id}", summary="Update person and passport data", status_code=status.HTTP_200_OK)
async def update_person_with_passport(
    person_id: int,
    data: PersonPatch,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> CommonResponse:
    await service.update_person_with_passport(person_id, data)
    return CommonResponse
