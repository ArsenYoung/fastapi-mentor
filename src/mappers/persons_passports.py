from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.schemas.passports import Passport
from src.schemas.persons import Person


def build_person_response(person: PersonsOrm, passport: PassportsOrm):
    return Person(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        passport=Passport.model_validate(passport)
    )
