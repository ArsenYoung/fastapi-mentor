from fastapi import APIRouter, Depends, status

from src.dependencies import get_students_courses_service
from src.schemas.common import CommonResponse
from src.schemas.students import StudentAddRequest, StudentPatch, StudentRead
from src.services.students_courses import StudentsCoursesService


router = APIRouter(prefix="/students", tags=["Студент и курсы М-М"])


@router.post("", summary="Добавить студента и его курсы", status_code=status.HTTP_201_CREATED)
async def post_student_with_courses(
    data: StudentAddRequest,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> CommonResponse:
    await service.create_student_with_courses(data)
    return CommonResponse

@router.get("{student_id}", summary="Получить студента и его курсы", response_model=StudentRead, status_code=status.HTTP_200_OK)
async def get_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> StudentRead:
    return await service.get_student_with_courses(student_id)

@router.delete("{student_id}", summary="Удалить студента и его курсы", status_code=status.HTTP_204_NO_CONTENT)
async def del_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> None:
    await service.del_student_with_courses(student_id)

@router.patch("{student_id}", summary="Обновить данные студента и его курсов", status_code=status.HTTP_200_OK)
async def del_student_with_courses(
    student_id: int,
    data: StudentPatch,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> CommonResponse:
    await service.update_student_with_courses(student_id, data)
    return CommonResponse
