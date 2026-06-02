from fastapi import APIRouter, Depends, status

from src.dependencies import get_persons_passports_service
from src.schemas.common import CommonResponse
from src.schemas.persons import PersonAddRequest, PersonPatch, PersonRead
from src.services.persons_passports import PersonsPassportsService


router = APIRouter(prefix="/persons", tags=["Люди и их паспортные данные 1-1"])


@router.post("", summary="Добавить человека с паспортными данными", status_code=status.HTTP_201_CREATED)
async def post_person_with_passport(
    data: PersonAddRequest,
    service: PersonsPassportsService = Depends(get_persons_passports_service)
) -> CommonResponse:
    await service.create_person_with_passport(data)
    return CommonResponse

@router.get("/{person_id}", response_model=PersonRead, summary="Получить человека и его пасспортные данные", status_code=status.HTTP_200_OK)
async def get_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> PersonRead:
    return await service.get_person_with_passport(person_id)

@router.delete("/{person_id}", summary="Удалить человека и его пасспортные данные", status_code=status.HTTP_204_NO_CONTENT)
async def del_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> None:
    await service.del_person_with_passport(person_id)

@router.patch("/{person_id}", summary="Изменить данные человека и его пасспорта", status_code=status.HTTP_200_OK)
async def update_person_with_passport(
    person_id: int,
    data: PersonPatch,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
) -> CommonResponse:
    await service.update_person_with_passport(person_id, data)
    return CommonResponse
