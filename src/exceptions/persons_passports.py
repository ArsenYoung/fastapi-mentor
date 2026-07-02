from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.schemas.errors import PassportErrorDetails, PersonErrorDetails


class PersonNotFoundException(ObjectNotFoundException):
    message = "Person not found"

    def __init__(self, *, person_id: int):
        super().__init__(
            details=PersonErrorDetails(person_id=person_id),
        )


class PassportAlreadyExistsException(AlreadyExistsException):
    message = "A person with this passport number already exists"

    def __init__(self, *, passport_number: str):
        super().__init__(
            details=PassportErrorDetails(passport_number=passport_number),
        )
