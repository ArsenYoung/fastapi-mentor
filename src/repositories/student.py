from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentsOrm]):
    model = StudentsOrm

    async def attach_course(self, student: StudentsOrm, course: CoursesOrm) -> None:
        link = next(
            (
                link
                for link in student.course_link
                if link.course_id == course.id
            ),
            None,
        )
        if link is not None and not link.is_deleted:
            return

        if link is not None:
            link.is_deleted = False
            link.courses = course
            return

        await self.create(
            StudentsCoursesOrm(
                student_id=student.id,
                course_id=course.id,
            )
        )

    async def detach_course(self, student: StudentsOrm, course: CoursesOrm) -> None:
        link = next(
            (
                link
                for link in student.course_link
                if link.course_id == course.id
            ),
            None,
        )
        if link is None or link.is_deleted:
            return

        link.is_deleted = True
