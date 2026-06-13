from pydantic import BaseModel, ConfigDict, Field

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "reestr_number": "2MMI",
            "title": "Mechanical Engineering",
        },
        {
            "reestr_number": "ICBN",
            "title": "Computer Science",
        },
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "reestr_number": "2MMI",
            "title": "Mechanical Engineering",
        },
        {
            "reestr_number": "ICBN",
            "title": "Computer Science",
        },
    ]
}


class CourseCreate(BaseModel):
    reestr_number: str = Field(min_length=1, max_length=4)
    title: str = Field(min_length=1, max_length=150)
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class Course(BaseModel):
    id: int
    reestr_number: str
    title: str
    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    reestr_number: str | None = None
    title: str | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )
