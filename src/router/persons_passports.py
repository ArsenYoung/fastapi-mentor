from fastapi import APIRouter, Depends

from src.dependencies import get_persons_passports_service
from src.schemas.persons import PersonAddRequest, PersonPatch, PersonRead
from src.services.persons_passports import PersonsPassportsService


router = APIRouter(prefix="/persons", tags=["Люди и их паспортные данные 1-1"])


@router.post("", summary="Добавить человека с паспортными данными", status_code=201)
async def post_person_with_passport(
    data: PersonAddRequest,
    service: PersonsPassportsService = Depends(get_persons_passports_service)
):
    await service.create_person_with_passport(data)
    return {"status": "ok"}

@router.get("/{person_id}", response_model=PersonRead, summary="Получить человека и его пасспортные данные", status_code=200)
async def get_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
):
    return await service.get_person_with_passport(person_id)

@router.delete("/{person_id}", summary="Удалить человека и его пасспортные данные", status_code=200)
async def del_person_with_passport(
    person_id: int,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
):
    await service.del_person_with_passport(person_id)
    return {"status": "ok"}

@router.patch("/{person_id}", summary="Изменить данные человека и его пасспорта", status_code=200)
async def update_person_with_passport(
    person_id: int,
    data: PersonPatch,
    service: PersonsPassportsService = Depends(get_persons_passports_service),
):
    await service.update_person_with_passport(person_id, data)
    return {"status": "ok"}
