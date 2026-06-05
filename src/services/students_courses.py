from collections import defaultdict

from sqlalchemy.exc import IntegrityError

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.repositories.students_courses import StudentsCoursesRepository
from src.schemas.courses import CourseAddRequest, CoursePatch
from src.schemas.students import Student, StudentAddRequest, StudentPatch, StudentsPage


class StudentsCoursesService:
    def __init__(self, repo: StudentsCoursesRepository):
        self.repo = repo

    def _unique_courses(
        self,
        courses: list[CourseAddRequest] | list[CoursePatch],
    ) -> list[CourseAddRequest | CoursePatch]:
        unique_courses: list[CourseAddRequest | CoursePatch] = []
        seen_reestr_numbers: set[str] = set()

        for course in courses:
            if not course.reestr_number:
                continue
            if course.reestr_number in seen_reestr_numbers:
                continue
            seen_reestr_numbers.add(course.reestr_number)
            unique_courses.append(course)

        return unique_courses

    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        student = await self.repo.get_student_by_record_book_number(data.record_book_number)

        if student is None:
            try:
                student = await self.repo.insert_student(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    record_book_number=data.record_book_number,
                )
            except IntegrityError as exc:
                raise AlreadyExistsException("A student with this record book number already exists") from exc
        elif student.is_deleted:
            await self.repo.restore_student(student.id)
            await self.repo.update_student(
                student.id,
                {
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "record_book_number": data.record_book_number,
                },
            )
        else:
            raise AlreadyExistsException("A student with this record book number already exists")

        for course_data in self._unique_courses(data.courses):
            course = await self.repo.get_course_by_reestr_number(course_data.reestr_number)

            if course is None:
                course = await self.repo.insert_course(
                    reestr_number=course_data.reestr_number,
                    title=course_data.title,
                )
            else:
                if course.is_deleted:
                    await self.repo.restore_course(course.id)
                if course.title != course_data.title:
                    await self.repo.update_course(course.id, {"title": course_data.title})

            await self.repo.attach_course_to_student(student.id, course.id)

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self.repo.get_student(student_id)
        if student is None:
            raise ObjectNotFoundException("Student not found")

        links = await self.repo.get_student_links(student_id)
        course_ids = [link.course_id for link in links]
        courses = await self.repo.get_courses_by_ids(course_ids)
        courses_by_id = {course.id: course for course in courses}
        for link in links:
            link.courses = courses_by_id.get(link.course_id)
        student.course_link = links
        return Student.model_validate(student)

    async def get_all_students_with_courses(self, limit: int, offset: int) -> StudentsPage:
        students, total = await self.repo.get_students_page(limit, offset)
        if not students:
            return StudentsPage(
                items=[],
                total=total,
                limit=limit,
                offset=offset,
            )

        student_ids = [student.id for student in students]
        links = await self.repo.get_students_links(student_ids)

        links_by_student_id: dict[int, list] = defaultdict(list)
        for link in links:
            links_by_student_id[link.student_id].append(link)

        course_ids = {link.course_id for link in links}
        courses = await self.repo.get_courses_by_ids(list(course_ids))
        courses_by_id = {course.id: course for course in courses}

        items: list[Student] = []
        for student in students:
            student_links = links_by_student_id.get(student.id, [])
            for link in student_links:
                link.courses = courses_by_id.get(link.course_id)
            student.course_link = student_links
            items.append(Student.model_validate(student))

        return StudentsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_student_with_courses(self, student_id: int) -> None:
        student = await self.repo.get_student(student_id)
        if student is None:
            raise ObjectNotFoundException("Student not found")

        current_links = await self.repo.get_student_links(student_id)
        course_ids = {link.course_id for link in current_links}

        await self.repo.soft_delete_student(student_id)

        for course_id in course_ids:
            await self.repo.detach_course_from_student(student_id, course_id)
            await self.repo.soft_delete_course_if_orphan(course_id)

    async def update_student_with_courses(self, student_id: int, data: StudentPatch) -> None:
        student = await self.repo.get_student(student_id)
        if student is None:
            raise ObjectNotFoundException("Student not found")

        student_data = data.model_dump(exclude_unset=True, exclude={"courses"})
        if student_data:
            try:
                await self.repo.update_student(student_id, student_data)
            except IntegrityError as exc:
                raise AlreadyExistsException("A student with this record book number already exists") from exc

        if data.courses is None:
            return

        current_links = await self.repo.get_student_links(student_id)
        current_course_ids = {link.course_id for link in current_links}
        requested_course_ids: set[int] = set()

        for course_data in self._unique_courses(data.courses):
            if course_data.title is None:
                continue

            course = await self.repo.get_course_by_reestr_number(course_data.reestr_number)

            if course is None:
                course = await self.repo.insert_course(
                    reestr_number=course_data.reestr_number,
                    title=course_data.title,
                )
            else:
                if course.is_deleted:
                    await self.repo.restore_course(course.id)
                if course.title != course_data.title:
                    await self.repo.update_course(course.id, {"title": course_data.title})

            await self.repo.attach_course_to_student(student_id, course.id)
            requested_course_ids.add(course.id)

        removed_course_ids = current_course_ids - requested_course_ids
        for course_id in removed_course_ids:
            await self.repo.detach_course_from_student(student_id, course_id)
            await self.repo.soft_delete_course_if_orphan(course_id)
