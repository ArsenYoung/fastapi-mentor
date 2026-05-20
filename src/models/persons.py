from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PersonsOrm(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    passport: Mapped["PassportsOrm"] = relationship(
        "PassportsOrm",
        back_populates="person",
        cascade="all, delete-orphan",
        single_parent=True,
    )
