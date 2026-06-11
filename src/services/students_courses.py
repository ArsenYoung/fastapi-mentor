from collections import defaultdict

from src.repositories.students_courses import StudentsCoursesRepository
from src.schemas.courses import CourseAddRequest
from src.schemas.students import (
    Student,
    StudentAddRequest,
    StudentCourseUpsertRequest,
    StudentPatch,
    StudentsPage,
)
from src.services.base import BaseService
from src.services.course import CourseService
from src.services.student import StudentService


class StudentsCoursesService(BaseService):
    def __init__(
        self,
        repo: StudentsCoursesRepository,
        student_service: StudentService,
        course_service: CourseService,
    ):
        self.repo = repo
        self.student_service = student_service
        self.course_service = course_service

    async def _get_or_create_active_course(
        self,
        data: CourseAddRequest | StudentCourseUpsertRequest,
    ):
        course = await self.course_service.get_any_by_reestr_number(data.reestr_number)
        if course is None:
            return await self.course_service.create(data)
        if course.is_deleted:
            await self.course_service.restore(course.id)
        if course.title != data.title:
            await self.course_service.update(course_id=course.id, data=data)
        return course

    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        student = await self.student_service.create_or_restore(data)
        for item in data.courses:
            course = await self._get_or_create_active_course(item)
            await self.repo.attach(student.id, course.id)

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self.student_service.get_active_by_id_or_raise(student_id)
        links = await self.repo.get_links_by_student_id(student_id)
        course_ids = [link.course_id for link in links]

        courses = []
        if course_ids:
            courses = await self.course_service.get_by_ids(course_ids)

        return Student(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            record_book_number=student.record_book_number,
            courses=courses,
        )
    
    async def get_all_students_with_courses(self, limit: int, offset: int) -> StudentsPage:
        students, total = await self.student_service.get_page(limit, offset)
        if not students:
            return StudentsPage(
                items=[], 
                total=total, 
                limit=limit, 
                offset=offset,
            )
        students_ids = [student.id for student in students]
        links = await self.repo.get_links_by_students_ids(students_ids)
        
        course_ids_by_student_id: dict[int, list[int]] = defaultdict(list)
        courses_ids: set[int] = set()
        for link in links:
            course_ids_by_student_id[link.student_id].append(link.course_id)
            courses_ids.add(link.course_id)
        
        courses_by_id = {}
        if courses_ids:
            courses = await self.course_service.get_by_ids(courses_ids)
            courses_by_id = {course.id: course for course in courses}

        items: list[Student] = []
        for student in students:
            student_course_ids = course_ids_by_student_id.get(student.id, [])
            student_courses = [
                courses_by_id[course_id]
                for course_id in student_course_ids
                if course_id in courses_by_id
            ]
            items.append(
                Student(
                    id=student.id,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    record_book_number=student.record_book_number,
                    courses=student_courses,
                )
            )
        
        return StudentsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_student_with_courses(self, student_id: int) -> None:
        await self.student_service.get_active_by_id_or_raise(student_id)
        links = await self.repo.get_links_by_student_id(student_id)
        for link in links:
            await self.repo.detach(student_id, link.course_id)
            if not await self.repo.has_active_links(link.course_id):
                await self.course_service.soft_delete(link.course_id)

        await self.student_service.soft_delete(student_id)
        
        

    async def update_student_with_courses(self, student_id: int, data: StudentPatch) -> None:
        student = await self.student_service.get_active_by_id_or_raise(student_id)
        student_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"courses"}
        )
        if student_data:
            await self.student_service.update(student_id, data)
        if data.courses is None:
            return

        existing_links = await self.repo.get_links_by_student_id(student.id)
        existing_course_ids = {link.course_id for link in existing_links}

        target_course_ids: set[int] = set()
        for item in data.courses:
            course = await self._get_or_create_active_course(item)
            target_course_ids.add(course.id)
            await self.repo.attach(student.id, course.id)

        course_ids_to_detach = existing_course_ids - target_course_ids
        for course_id in course_ids_to_detach:
            await self.repo.detach(student.id, course_id)
            if not await self.repo.has_active_links(course_id):
                await self.course_service.soft_delete(course_id)
