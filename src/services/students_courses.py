from sqlalchemy.exc import IntegrityError

from src.exceptions import CourseConflictError, StudentConflictError, StudentNotFoundError
from src.mappers.students_courses import build_student_response
from src.repositories.courses import CoursesRepository
from src.repositories.students import StudentsRepository
from src.repositories.students_courses_m2m import StudentsCoursesRepository
from src.schemas.courses import CourseAddRequest
from src.schemas.students import Student, StudentAddRequest, StudentPatch
from src.schemas.students_courses_m2m import StudentsCoursesAdd


class StudentsCoursesService():
    def __init__(self, session):
        self.students_repo = StudentsRepository(session)
        self.courses_repo = CoursesRepository(session)
        self.students_courses_repo = StudentsCoursesRepository(session)

    async def _get_student(self, **filter_by) -> Student:
        student = await self.students_repo.get_one_or_none(**filter_by)
        if student is None:
            raise StudentNotFoundError()
        return student
    
    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        try:
            student_response = await self.students_repo.add(data, exclude={"courses"})
        except IntegrityError as exc:
            raise StudentConflictError() from exc
        
        course_data = [
            CourseAddRequest(
                reestr_number=course.reestr_number, 
                title=course.title)
            for course in data.courses
        ]
        for course in course_data:
            try:
                course_response = await self.courses_repo.add(course)
            except IntegrityError as exc:
                raise CourseConflictError() from exc
            
            await self.students_courses_repo.add(
                StudentsCoursesAdd(
                    student_id=student_response.id,
                    course_id=course_response.id,
                )
            )

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self._get_student(id=student_id)
        m2m_data = await self.students_courses_repo.get_all(student_id=student_id)
        courses = []
        for link in m2m_data:
            course = await self.courses_repo.get_one_or_none(id=link.course_id)
            if course is not None:
                courses.append(course)
        return build_student_response(student, courses)
    
    async def del_student_with_courses(self, student_id: int) -> None:
        await self._get_student(id=student_id)
        m2m_data = await self.students_courses_repo.get_all(student_id=student_id)
        course_ids = [link.course_id for link in m2m_data]
        if course_ids:
            await self.courses_repo.delete_bulk_by_ids(course_ids)
        await self.students_courses_repo.delete(student_id=student_id)
        await self.students_repo.delete(id=student_id)
        
    async def update_student_with_courses(self, student_id, data: StudentPatch) -> None:
        await self._get_student(id=student_id)
        student_data = data.model_dump(
            exclude_unset=True,
            exclude={"courses"},
        )
        if student_data:
            try:
                await self.students_repo.update(student_data, id=student_id)
            except IntegrityError as exc:
                raise StudentConflictError() from exc

        if data.courses is not None:
            for course in data.courses:
                course_data = course.model_dump()
                existing_course = await self.courses_repo.get_one_or_none(
                    reestr_number=course.reestr_number
                )
                if existing_course is None:
                    try:
                        course_response = await self.courses_repo.add(
                            CourseAddRequest(**course_data)
                        )
                    except IntegrityError as exc:
                        raise CourseConflictError() from exc
                else:
                    try:
                        await self.courses_repo.update(
                            course_data,
                            id=existing_course.id,
                        )
                    except IntegrityError as exc:
                        raise CourseConflictError() from exc
                    course_response = existing_course

                link = await self.students_courses_repo.get_one_or_none(
                    student_id=student_id,
                    course_id=course_response.id,
                )
                if link is None:
                    await self.students_courses_repo.add(
                        StudentsCoursesAdd(
                            student_id=student_id,
                            course_id=course_response.id,
                        )
                    )
    
        
