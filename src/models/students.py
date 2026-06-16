from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.students_courses import StudentsCoursesOrm


class StudentsOrm(Base):
    __tablename__ = "students"

    __table_args__ = (
        Index(
            "uq_students_record_book_number_active",
            "record_book_number",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_book_number: Mapped[str] = mapped_column(String(8), nullable=False)
    course_link = relationship(
        "StudentsCoursesOrm", back_populates="students", cascade="all, delete-orphan"
    )
    courses = relationship(
        "CoursesOrm",
        secondary=StudentsCoursesOrm.__table__,
        primaryjoin=(
            "and_("
            "StudentsOrm.id == StudentsCoursesOrm.student_id, "
            "StudentsCoursesOrm.is_deleted.is_(False)"
            ")"
        ),
        secondaryjoin=(
            "and_("
            "CoursesOrm.id == StudentsCoursesOrm.course_id, "
            "CoursesOrm.is_deleted.is_(False)"
            ")"
        ),
        overlaps="course_link,courses,student_link,students",
    )
