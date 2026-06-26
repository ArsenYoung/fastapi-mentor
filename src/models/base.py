from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeMeta, registry

metadata = sa.MetaData()
mapped_registry = registry(metadata=metadata)


class BaseServiceModel:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="False",
    )

Base: DeclarativeMeta = mapped_registry.generate_base(cls=BaseServiceModel)
AssociationBase = mapped_registry.generate_base()
