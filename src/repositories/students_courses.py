from dataclasses import dataclass

from sqlalchemy import select, update

from src.mappers.students_courses import build_student_response
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.schemas.students import Student, StudentAddRequest, StudentPatch

@dataclass(slots=True)
class UpdateStudentResult:
    student_found: bool
    courses_found: bool


class StudentsCoursesRepository():
    def __init__(self, session):
        self.session = session

    async def get_student(self, student_id: int) -> Student:
        student = await self.session.execute(
            select(StudentsOrm).filter_by(
                id=student_id,
                is_deleted=False
            ))
        student_response = student.scalar_one_or_none()
        return student_response

    async def create_student_with_courses(self, data: StudentAddRequest) -> None:
        student = StudentsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
            record_book_number=data.record_book_number
        )
        self.session.add(student)
        await self.session.flush()

        seen_reestr_numbers: set[str] = set()

        for item in data.courses:
            if item.reestr_number in seen_reestr_numbers:
                continue
            seen_reestr_numbers.add(item.reestr_number)
            result = await self.session.execute(
                select(CoursesOrm).filter_by(
                    reestr_number=item.reestr_number,
                    is_deleted=False
                )
            )
            course = result.scalar_one_or_none()

            if course is None:
                course = CoursesOrm(
                    reestr_number=item.reestr_number,
                    title=item.title
                )
                self.session.add(course)
                await self.session.flush()

            self.session.add(
                StudentsCoursesOrm(
                    student_id=student.id,
                    course_id=course.id
                )
            )
    
    async def get_student_with_courses(self, student_id: int) -> Student | None:
        student = await self.get_student(student_id)

        if student is None:
            return None
        
        m2m = await self.session.execute(
            select(StudentsCoursesOrm).filter_by(
                student_id=student.id,
            ))
        m2m_response = m2m.scalars().all()

        courses = []
        for link in m2m_response:
            course = await self.session.execute(
                select(CoursesOrm).filter_by(
                    id=link.course_id
            ))
            course_response = course.scalar_one_or_none()
            if course_response is not None:
                courses.append(course_response)

        return build_student_response(student, courses)
    
    async def del_student_with_courses(self, student_id: int) -> bool:
        student = await self.get_student(student_id)
        if student is None:
            return False
        await self.session.execute(
            update(StudentsOrm)
            .filter_by(id=student_id)
            .values(is_deleted=True)
        )
        m2m = await self.session.execute(
            select(StudentsCoursesOrm).filter_by(
                student_id=student.id,
            ))
        m2m_response = m2m.scalars().all()

        await self.session.execute(
            update(StudentsCoursesOrm)
            .filter_by(student_id=student_id)
            .values(is_deleted=True)
        )

        for item in m2m_response:
            await self.session.execute(
                update(CoursesOrm)
                .filter_by(id=item.course_id)
                .values(is_deleted=True)
            )
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
            await self.session.execute(
                update(StudentsOrm)
                .filter_by(id=student_id)
                .values(**student_data)
            )

        if data.courses is not None:
            for item in data.courses:
                course_result = await self.session.execute(
                    select(CoursesOrm)
                    .filter_by(
                        reestr_number=item.reestr_number,
                        is_deleted=False
                    )
                )
                course = course_result.scalar_one_or_none()

                if course is None:
                    return UpdateStudentResult(
                        student_found=True,
                        courses_found=False
                    )
                
                await self.session.execute(
                    update(CoursesOrm)
                    .filter_by(id=course.id)
                    .values(
                        reestr_number=item.reestr_number,
                        title=item.title
                    )
                )

        return UpdateStudentResult(
            student_found=True,
            courses_found=True
        )

