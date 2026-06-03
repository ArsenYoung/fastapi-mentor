class AppError(Exception):
    code = "unexpected_error"
    message = "Неизвестная ошибка"
    details = None

class NotFoundError(AppError):
    code = "object_not_found_error"
    message = "Объект не найден"

class ConflictError(AppError):
    code = "conflict_error"
    message = "Конфликт"

class AuthorNotFoundError(NotFoundError):
    code = "author_not_found_error"
    message = "Автор не найден"

class BookNotFoundError(NotFoundError):
    code = "book_not_found_error"
    message = "Книга не найдена"

class AuthorConflictError(ConflictError):
    code = "author_conflict_error"
    message = "Автор с таким именем уже существует"

class PersonNotFoundError(NotFoundError):
    code = "person_not_found_error"
    message = "Человек не найден"

class PassportNotFoundError(NotFoundError):
    code = "passport_not_found_error"
    message = "Паспорт не найден"

class PassportConflictError(ConflictError):
    code = "passport_conflict_error"
    message = "Номер паспорта уже существует"

class StudentNotFoundError(NotFoundError):
    code = "student_not_found_error"
    message = "Студент не найден"

class CourseNotFoundError(NotFoundError):
    code = "course_not_found_error"
    message = "Курс не найден"

class StudentConflictError(ConflictError):
    code = "student_conflict_error"
    message = "Студент уже существует"

class CourseConflictError(ConflictError):
    code = "course_conflict_error"
    message = "Курс уже существует"
