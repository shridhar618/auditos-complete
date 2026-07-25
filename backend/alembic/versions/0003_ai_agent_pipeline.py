"""AI agent pipeline: policy_rules, agent_run_logs, investigation evidence/recommendation columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23
"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

policy_rule_type_enum = postgresql.ENUM("amount_threshold", "department_threshold", name="policy_rule_type")


def upgrade() -> None:
    bind = op.get_bind()
    policy_rule_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "policy_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("rule_type", policy_rule_type_enum, nullable=False),
        sa.Column("threshold_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_policy_rules_organization_id", "policy_rules", ["organization_id"])

    op.create_table(
        "agent_run_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("investigation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_name", sa.String(50), nullable=False),
        sa.Column("step_order", sa.Integer, nullable=False),
        sa.Column("input_summary", sa.Text, nullable=True),
        sa.Column("output_summary", sa.Text, nullable=True),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("used_llm", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agent_run_logs_organization_id", "agent_run_logs", ["organization_id"])
    op.create_index("ix_agent_run_logs_investigation_id", "agent_run_logs", ["investigation_id"])

    op.add_column("investigations", sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column("investigations", sa.Column("evidence_json", postgresql.JSONB, nullable=True))
    op.add_column("investigations", sa.Column("recommendation", sa.Text, nullable=True))
    op.add_column("investigations", sa.Column("resolution_notes", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("investigations", "resolution_notes")
    op.drop_column("investigations", "recommendation")
    op.drop_column("investigations", "evidence_json")
    op.drop_column("investigations", "approved_by_user_id")
    op.drop_table("agent_run_logs")
    op.drop_table("policy_rules")
    policy_rule_type_enum.drop(op.get_bind(), checkfirst=True)
