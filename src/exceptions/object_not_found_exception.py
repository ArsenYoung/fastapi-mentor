from src.exceptions.app_exception import AppException


class ObjectNotFoundException(AppException):
    code = "object_not_found_exception"
    message = "Object not found"

