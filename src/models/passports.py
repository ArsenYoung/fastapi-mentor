from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PassportsOrm(Base):
    __tablename__ = "passports"

    __table_args__ = (
        Index(
            "uq_passports_number_active",
            "number",
            unique=True,
            postgresql_where=text("is_deleted = False"),
        ),
        Index(
            "uq_passports_person_id_active",
            "person_id",
            unique=True,
            postgresql_where=text("is_deleted = False"),
        ),
    )

    number: Mapped[str] = mapped_column(
        String(10), 
        nullable=False,
    )
    registrated_in: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
    )

    person: Mapped["PersonsOrm"] = relationship(
        back_populates="passport",
    )
