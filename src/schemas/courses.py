from pydantic import BaseModel, ConfigDict, Field


class CourseAddRequest(BaseModel):
    reestr_number: str = Field(min_length=1, max_length=4)
    title: str = Field(min_length=1, max_length=150)
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "reestr_number": "2MMI",
                    "title": "Машиностроение",
                },
                { 
                    "reestr_number": "ICBN",
                    "title": "Информатика",
                },
            ]
        }
    )

class CourseRead(BaseModel):
    id: int
    reestr_number: str
    title: str

class Course(CourseRead):
    model_config = ConfigDict(from_attributes=True)

class CoursePatch(BaseModel):
    reestr_number: str
    title: str
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "reestr_number": "2MMI",
                    "title": "Машиностроение",
                },
                { 
                    "reestr_number": "ICBN",
                    "title": "Информатика",
                },
            ]
        }
    )
