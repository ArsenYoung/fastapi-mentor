from sqlalchemy.exc import IntegrityError
from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.schemas.students import Student, StudentAddRequest, StudentPatch, StudentsPage


class StudentsCoursesService():
    def __init__(self, repo):
        self.repo = repo
    
    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        try:
            await self.repo.create_student_with_courses(data)
        except IntegrityError as exc:
            raise AlreadyExistsException("A student with this record book number already exists")

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            raise ObjectNotFoundException("Student not found")
        return student
    
    async def get_all_students_with_courses(self, limit: int, offset: int) -> StudentsPage:
        items, total = await self.repo.get_all_students_with_courses(limit, offset)
        return StudentsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
        
    async def del_student_with_courses(self, student_id: int) -> None:
        is_deleted = await self.repo.del_student_with_courses(student_id)
        if not is_deleted:
            raise ObjectNotFoundException("Student not found")
        
    async def update_student_with_courses(self, student_id: int, data: StudentPatch) -> None:
        try:
            result = await self.repo.update_student_with_courses(student_id, data)
        except IntegrityError as exc:
            raise AlreadyExistsException("A student with this record book number already exists")
        
        if not result.student_found:
            raise ObjectNotFoundException("Student not found")
        
        if not result.courses_found:
            raise ObjectNotFoundException("Course not found")
