from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PassportsOrm(Base):
    __tablename__ = "passports"

    number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    registrated_in: Mapped[str] = mapped_column(String(200), nullable=False)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    person: Mapped["PersonsOrm"] = relationship(
        "PersonsOrm",
        back_populates="passport",
    )
