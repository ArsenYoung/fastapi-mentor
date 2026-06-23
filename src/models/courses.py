from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CoursesOrm(Base):
    __tablename__ = "courses"

    __table_args__ = (
        Index(
            "uq_courses_reestr_number_active",
            "reestr_number",
            unique=True,
            postgresql_where=text("is_deleted = false")
        ),
    )

    reestr_number: Mapped[str] = mapped_column(
        String(4),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    student_link = relationship(
        "StudentsCoursesOrm",
        back_populates="courses",
        cascade="all, delete-orphan",
        primaryjoin="and_(CoursesOrm.id == StudentsCoursesOrm.course_id, StudentsCoursesOrm.is_deleted.is_(False))",
        lazy="selectin",
    )
