from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException


class PassportAlreadyExistsException(AlreadyExistsException):
    code = "passport_already_exists_exception"
    message = "A person with this passport number already exists"


class PersonNotFoundException(ObjectNotFoundException):
    code = "person_not_found_exception"
    message = "Person not found"
