import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AgentRunLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    One row per agent step, per pipeline run. This is the "memory and
    logs" every agent in the master spec is required to have: what it
    was given (input_summary/input_json), what it produced
    (output_summary/output_json), and why (reasoning) - fully auditable
    and replayable, which matters a lot for an audit product.
    """
    __tablename__ = "agent_run_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    investigation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
    )

    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)   # "detection", "policy", "investigation", "evidence", "recommendation"
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    input_summary: Mapped[str] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=True)
    used_llm: Mapped[bool] = mapped_column(default=False, nullable=False)
