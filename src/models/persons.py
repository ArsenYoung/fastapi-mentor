from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PersonsOrm(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
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
    passport: Mapped["PassportsOrm"] = relationship(
        "PassportsOrm",
        back_populates="person",
        cascade="all, delete-orphan",
        single_parent=True,
    )
