from http import HTTPStatus
from pydantic import BaseModel


class CommonResponse(BaseModel):
    status: str = HTTPStatus.OK.phrase.lower()