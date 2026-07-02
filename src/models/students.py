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
            postgresql_where=text("is_deleted = False"),
        ),
    )

    first_name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
    )
    record_book_number: Mapped[str] = mapped_column(
        String(8), 
        nullable=False,
    )
    
    courses: Mapped[set["CoursesOrm"]] = relationship(
        secondary="students_courses",
        back_populates="students",
        collection_class=set,
        lazy="selectin",
    )
