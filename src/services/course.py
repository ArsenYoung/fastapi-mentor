from sqlalchemy.exc import IntegrityError

from src.models.courses import CoursesOrm
from src.repositories.course import CourseRepository
from src.schemas.courses import CourseAddRequest, CoursePatch
from src.services.base import BaseService


class CourseService(BaseService):
    course_not_found_msg = "Course not found"
    course_already_exists_msg = "A course with this reestr number already exists"
    course_unique_constraint = "uq_courses_reestr_number_active"

    def __init__(self, repo: CourseRepository):
        self.repo = repo

    def _is_course_unique_error(self, exc: IntegrityError) -> bool:
        return self.course_unique_constraint in str(exc)

    async def get_active_by_id_or_raise(self, course_id: int) -> CoursesOrm:
        course = await self.repo.get_by_id_active(course_id)
        if course is None:
            self._raise_not_found(
                self.course_not_found_msg,
                course_id=course_id
            )
        return course

    async def get_any_by_reestr_number(self, reestr_number: str) -> CoursesOrm | None:
        return await self.repo.get_by_reestr_number(reestr_number)
    
    async def get_by_ids(self, course_ids: list[int]) -> list[CoursesOrm]:
        return await self.repo.get_by_ids(course_ids)
    
    async def create(self, data: CourseAddRequest) -> CoursesOrm:
        try:
            return await self.repo.insert(
                reestr_number=data.reestr_number,
                title=data.title,
            )
        except IntegrityError as exc:
            if self._is_course_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.course_already_exists_msg,
                    reestr_number=data.reestr_number,

                )
            raise

    async def update(self, course_id: int, data: CoursePatch) -> None:
        await self.get_active_by_id_or_raise(course_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )
        if not values:
            return
        try:
            await self.repo.update(course_id, values)
        except IntegrityError as exc:
            if self._is_course_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.course_already_exists_msg,
                    course_id=course_id,
                    reestr_number=values.get("reestr_number")
                )
            raise

    async def soft_delete(self, course_id: int) -> None:
        await self.get_active_by_id_or_raise(course_id)
        await self.repo.soft_delete(course_id)

    async def restore(self, course_id: int) -> None:
        course = await self.repo.get_by_id_any(course_id)
        if course is None:
            self._raise_not_found(
                self.course_not_found_msg,
                course_id=course_id
            )
        try:
            await self.repo.restore(course_id)
        except IntegrityError as exc:
            if self._is_course_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.course_already_exists_msg,
                    course_id=course_id,
                    reestr_number=course.reestr_number,
                )
            raise
