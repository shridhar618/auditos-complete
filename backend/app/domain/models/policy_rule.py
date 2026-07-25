import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class PolicyRuleType(str, enum.Enum):
    AMOUNT_THRESHOLD = "amount_threshold"        # flags any transaction over `threshold_amount`
    DEPARTMENT_THRESHOLD = "department_threshold"  # flags if over threshold AND scoped to one department


class PolicyRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A single, machine-checkable compliance rule. This is intentionally
    simple (threshold-based) - it is NOT the full Policy Center (that
    phase adds uploaded PDF/DOCX policies with pgvector semantic search
    and citations). This table is what the Policy Agent evaluates
    against every transaction the Detection Agent flags.
    """
    __tablename__ = "policy_rules"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    rule_type: Mapped[PolicyRuleType] = mapped_column(Enum(PolicyRuleType, name="policy_rule_type", values_callable=enum_values), nullable=False)
    threshold_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
