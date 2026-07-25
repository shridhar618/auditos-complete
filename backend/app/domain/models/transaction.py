import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class TransactionStatus(str, enum.Enum):
    NORMAL = "normal"
    FLAGGED = "flagged"
    UNDER_INVESTIGATION = "under_investigation"
    VIOLATION = "violation"
    CLEARED = "cleared"


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A single financial transaction ingested for continuous monitoring.
    risk_score (0-100) and status are set by the Detection Agent in the
    AI pipeline (a later phase) - for now they're populated by the demo
    seeder so the Dashboard module has real rows to aggregate.
    """
    __tablename__ = "transactions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True
    )

    reference_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status", values_callable=enum_values), nullable=False, default=TransactionStatus.NORMAL
    )
    risk_score: Mapped[int] = mapped_column(nullable=False, default=0)  # 0-100
    is_policy_violation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
