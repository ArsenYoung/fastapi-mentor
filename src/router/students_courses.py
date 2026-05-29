from fastapi import APIRouter, Depends

from src.dependencies import get_students_courses_service
from src.schemas.students import StudentAddRequest, StudentPatch
from src.services.students_courses import StudentsCoursesService


router = APIRouter(prefix="/students", tags=["Студент и курсы М-М"])


@router.post("", summary="Добавить студента и его курсы", status_code=201)
async def post_student_with_courses(
    data: StudentAddRequest,
    service: StudentsCoursesService = Depends(get_students_courses_service)
):
    await service.create_student_with_courses(data)
    return {"status": "ok"}

@router.get("{student_id}", summary="Получить студента и его курсы", status_code=200)
async def get_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
):
    return await service.get_student_with_courses(student_id)

@router.delete("{student_id}", summary="Удалить студента и его курсы", status_code=200)
async def del_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
):
    await service.del_student_with_courses(student_id)
    return {"status": "ok"}

@router.patch("{student_id}", summary="Обновить данные студента и его курсов", status_code=200)
async def del_student_with_courses(
    student_id: int,
    data: StudentPatch,
    service: StudentsCoursesService = Depends(get_students_courses_service)
):
    await service.update_student_with_courses(student_id, data)
    return {"status": "ok"}
