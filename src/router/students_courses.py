from fastapi import APIRouter, Depends, Query, status

from src.dependencies import get_students_courses_service
from src.schemas.common import CommonResponse
from src.schemas.students import StudentAddRequest, StudentPatch, StudentRead, StudentsPage
from src.services.students_courses import StudentsCoursesService


router = APIRouter(prefix="/students", tags=["Students and Courses M-M"])


@router.post("", summary="Create a student and their courses", status_code=status.HTTP_201_CREATED)
async def post_student_with_courses(
    data: StudentAddRequest,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> CommonResponse:
    await service.create_student_with_courses(data)
    return CommonResponse

@router.get("{student_id}", summary="Get a student and their courses", response_model=StudentRead, status_code=status.HTTP_200_OK)
async def get_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> StudentRead:
    return await service.get_student_with_courses(student_id)

@router.get("", summary="Get students and their courses", response_model=StudentsPage, status_code=status.HTTP_200_OK)
async def get_all_students_with_courses(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    service: StudentsCoursesService = Depends(get_students_courses_service)
):
    return await service.get_all_students_with_courses(limit, offset)

@router.delete("{student_id}", summary="Delete a student and their courses", status_code=status.HTTP_204_NO_CONTENT)
async def del_student_with_courses(
    student_id: int,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> None:
    await service.del_student_with_courses(student_id)

@router.patch("{student_id}", summary="Update student and course data", status_code=status.HTTP_200_OK)
async def del_student_with_courses(
    student_id: int,
    data: StudentPatch,
    service: StudentsCoursesService = Depends(get_students_courses_service)
) -> CommonResponse:
    await service.update_student_with_courses(student_id, data)
    return CommonResponse
