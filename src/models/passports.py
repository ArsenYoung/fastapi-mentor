from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base

class PassportsOrm(Base):
    __tablename__ = "passports"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(15), nullable=False)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    person: Mapped["PersonsOrm"] = relationship(
        "PersonsOrm",
        back_populates="passport",
    )
