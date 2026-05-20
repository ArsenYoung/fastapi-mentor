from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.courses_students import courses_students


class StudentsOrm(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    courses: Mapped[list["CoursesOrm"]] = relationship(
        "CoursesOrm",
        secondary=courses_students,
        back_populates="students",
        passive_deletes=True,
    )
