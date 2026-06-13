from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException


class StudentAlreadyExistsException(AlreadyExistsException):
    code = "student_already_exists_exception"
    message = "A student with this record book number already exists"


class CourseAlreadyExistsException(AlreadyExistsException):
    code = "course_already_exists_exception"
    message = "A course with this reestr number already exists"


class StudentNotFoundException(ObjectNotFoundException):
    code = "student_not_found_exception"
    message = "Student not found"
