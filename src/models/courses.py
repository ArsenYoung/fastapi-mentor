from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.courses_students import courses_students


class CoursesOrm(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    students: Mapped[list["StudentsOrm"]] = relationship(
        "StudentsOrm",
        secondary=courses_students,
        back_populates="courses",
        passive_deletes=True,
    )
