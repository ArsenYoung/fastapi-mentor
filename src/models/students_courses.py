from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class StudentsCoursesOrm(Base):
    __tablename__ = "students_courses"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True
    )

    students = relationship("StudentsOrm", back_populates="course_link")
    courses = relationship("CoursesOrm", back_populates="student_link")
