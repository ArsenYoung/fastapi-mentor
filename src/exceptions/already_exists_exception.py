from src.exceptions.app_exception import AppException


class AlreadyExistsException(AppException):
    code = "already_exists_exception"
    message = "Object already exists"