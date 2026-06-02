from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.schemas.courses import Course
from src.schemas.students import Student


def build_student_response(student: StudentsOrm, courses: list[CoursesOrm]) -> Student:
    return Student(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        record_book_number=student.record_book_number,
        courses=[Course.model_validate(course) for course in courses]
    )
