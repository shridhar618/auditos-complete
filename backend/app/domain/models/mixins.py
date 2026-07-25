"""Reusable mixins so every table gets a consistent PK + audit timestamps."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    """
    Pass as `values_callable` to every sa.Enum(SomeStrEnum, ...) column.

    SQLAlchemy's Enum type binds a Python enum's NAME by default (e.g.
    "OPEN"), not its value ("open"). Every migration in this project
    creates native Postgres enum types using lowercase values, so without
    this, every write to an enum column would fail at runtime with
    "invalid input value for enum". This must be passed to every
    Enum(...) column definition in every model.
    """
    return [e.value for e in enum_cls]


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
