from datetime import datetime

from sqlalchemy import Index, String, DateTime, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class StudentsOrm(Base):
    __tablename__ = "students"

    __table_args__ = (
        Index(
            "uq_students_record_book_number_active",
            "record_book_number",
            unique=True,
            postgresql_where=text("is_deleted = false")
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_book_number: Mapped[str] = mapped_column(String(8), nullable=False)
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
    course_link = relationship(
        "StudentsCoursesOrm",
        back_populates="students",
        cascade="all, delete-orphan"
    )
