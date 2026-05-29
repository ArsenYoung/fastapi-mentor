from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, func, text
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

    id: Mapped[int] = mapped_column(primary_key=True)
    reestr_number: Mapped[str] = mapped_column(
        String(4), 
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(150), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False
    )
    student_link = relationship(
        "StudentsCoursesOrm",
        back_populates="courses",
        cascade="all, delete-orphan",
    )
