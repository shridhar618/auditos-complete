import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class InvestigationStatus(str, enum.Enum):
    OPEN = "open"
    PENDING_APPROVAL = "pending_approval"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Investigation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A human-in-the-loop case opened against a flagged transaction.
    Populated by the AI Agent pipeline (Detection -> Policy ->
    Investigation -> Evidence -> Recommendation) and always ends in
    PENDING_APPROVAL - a human must explicitly resolve or dismiss it;
    the pipeline never self-approves.
    """
    __tablename__ = "investigations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[InvestigationStatus] = mapped_column(
        Enum(InvestigationStatus, name="investigation_status", values_callable=enum_values), nullable=False, default=InvestigationStatus.OPEN
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level", values_callable=enum_values), nullable=False, default=RiskLevel.MEDIUM
    )
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSONB, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    transaction: Mapped["Transaction | None"] = relationship(foreign_keys=[transaction_id])  # noqa: F821
