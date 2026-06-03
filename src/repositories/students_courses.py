from dataclasses import dataclass

from sqlalchemy import select

from src.mappers.students_courses import build_student_response
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository
from src.schemas.students import Student, StudentAddRequest, StudentPatch


@dataclass(slots=True)
class UpdateStudentResult:
    student_found: bool
    courses_found: bool


class StudentsCoursesRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def _get_or_restore_course(self, reestr_number: str, title: str) -> CoursesOrm:
        result = await self.session.execute(
            select(CoursesOrm)
            .filter_by(reestr_number=reestr_number)
            .order_by(
                CoursesOrm.is_deleted.asc(),
                CoursesOrm.id.desc(),
            )
        )
        course = result.scalars().first()

        if course is None:
            course = await self.insert_instance(
                CoursesOrm(
                    reestr_number=reestr_number,
                    title=title,
                )
            )
            return course

        if course.is_deleted:
            course.is_deleted = False
            await self.session.flush()

        return course

    async def _attach_course_to_student(self, student_id: int, course_id: int) -> None:
        active_link = await self.fetch_active_one(
            StudentsCoursesOrm,
            student_id=student_id,
            course_id=course_id,
        )
        if active_link is not None:
            return

        existing_link = await self.fetch_one(
            select(StudentsCoursesOrm).filter_by(
                student_id=student_id,
                course_id=course_id,
            )
        )

        if existing_link is None:
            self.session.add(
                StudentsCoursesOrm(
                    student_id=student_id,
                    course_id=course_id,
                )
            )
            return

        await self.update_where(
            StudentsCoursesOrm,
            {"is_deleted": False},
            student_id=student_id,
            course_id=course_id,
        )

    async def _soft_delete_orphan_courses(self, course_ids: set[int]) -> None:
        for course_id in course_ids:
            active_link = await self.fetch_active_one(
                StudentsCoursesOrm,
                course_id=course_id,
            )
            if active_link is None:
                await self.soft_delete_where(
                    CoursesOrm,
                    id=course_id,
                )

    async def get_student(self, student_id: int) -> Student | None:
        return await self.fetch_active_one(StudentsOrm, id=student_id)

    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        student = await self.insert_instance(
            StudentsOrm(
                first_name=data.first_name,
                last_name=data.last_name,
                record_book_number=data.record_book_number
            )
        )

        seen_reestr_numbers: set[str] = set()
        for item in data.courses:
            if item.reestr_number in seen_reestr_numbers:
                continue
            seen_reestr_numbers.add(item.reestr_number)

            course = await self._get_or_restore_course(item.reestr_number, item.title)
            await self._attach_course_to_student(student.id, course.id)

    async def get_student_with_courses(self, student_id: int) -> Student | None:
        student = await self.get_student(student_id)
        if student is None:
            return None

        m2m = await self.fetch_active_all(
            StudentsCoursesOrm,
            student_id=student.id,
        )

        courses = []
        for link in m2m:
            course = await self.fetch_active_one(
                CoursesOrm,
                id=link.course_id,
            )
            if course is not None:
                courses.append(course)

        return build_student_response(student, courses)

    async def del_student_with_courses(self, student_id: int) -> bool:
        student = await self.get_student(student_id)
        if student is None:
            return False

        linked_courses = await self.fetch_active_all(
            StudentsCoursesOrm,
            student_id=student_id,
        )
        course_ids = {link.course_id for link in linked_courses}

        await self.soft_delete_where(
            StudentsOrm,
            id=student_id,
        )
        await self.soft_delete_where(
            StudentsCoursesOrm,
            student_id=student_id,
        )
        await self._soft_delete_orphan_courses(course_ids)
        return True

    async def update_student_with_courses(self, student_id: int, data: StudentPatch) -> UpdateStudentResult:
        student = await self.get_student(student_id)
        if student is None:
            return UpdateStudentResult(
                student_found=False,
                courses_found=False
            )

        student_data = data.model_dump(
            exclude_unset=True,
            exclude={"courses"},
        )
        if student_data:
            await self.update_where(
                StudentsOrm,
                student_data,
                id=student_id,
            )

        if data.courses is not None:
            requested_course_ids: set[int] = set()
            seen_reestr_numbers: set[str] = set()
            current_links = await self.fetch_active_all(
                StudentsCoursesOrm,
                student_id=student_id,
            )
            current_course_ids = {link.course_id for link in current_links}

            for item in data.courses:
                if item.reestr_number in seen_reestr_numbers:
                    continue
                seen_reestr_numbers.add(item.reestr_number)

                course = await self._get_or_restore_course(
                    item.reestr_number,
                    item.title,
                )
                requested_course_ids.add(course.id)
                await self._attach_course_to_student(student_id, course.id)

            removed_course_ids = current_course_ids - requested_course_ids

            for link in current_links:
                if link.course_id in removed_course_ids:
                    await self.soft_delete_where(
                        StudentsCoursesOrm,
                        student_id=student_id,
                        course_id=link.course_id,
                    )

            await self._soft_delete_orphan_courses(removed_course_ids)

        return UpdateStudentResult(
            student_found=True,
            courses_found=True
        )
