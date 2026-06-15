from src.exceptions.app_exception import AppException


class AlreadyExistsException(AppException):
    message = "Object already exists"
