from pydantic import BaseModel

    
class StudentsCoursesAdd(BaseModel):
    student_id: int
    course_id: int