from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PersonsOrm(Base):
    __tablename__ = "persons"

    first_name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
    )

    passport: Mapped["PassportsOrm"] = relationship(
        back_populates="person",
        primaryjoin="and_(PersonsOrm.id == PassportsOrm.person_id, PassportsOrm.is_deleted.is_(False))",
        cascade="all, delete-orphan",
        uselist=False,
    )
