from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AssociationBase


class StudentsCoursesOrm(AssociationBase):
    __tablename__ = "students_courses"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    students = relationship("StudentsOrm", back_populates="course_link")
    courses = relationship(
        "CoursesOrm",
        back_populates="student_link",
        primaryjoin="and_(StudentsCoursesOrm.course_id == CoursesOrm.id, CoursesOrm.is_deleted.is_(False))",
        lazy="joined",
    )
