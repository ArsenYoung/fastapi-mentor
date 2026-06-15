from src.exceptions.app_exception import AppException


class ObjectNotFoundException(AppException):
    message = "Object not found"
