from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


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
        "StudentsCoursesOrm",
        back_populates="students",
        cascade="all, delete-orphan",
    )

    @property
    def courses(self) -> list["CoursesOrm"]:
        return [
            link.courses
            for link in self.course_link
            if not link.is_deleted
            and link.courses is not None
            and not link.courses.is_deleted
        ]
