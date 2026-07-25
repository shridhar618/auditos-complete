"""dashboard foundation: departments, vendors, transactions, investigations

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-23
"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

transaction_status_enum = postgresql.ENUM(
    "normal", "flagged", "under_investigation", "violation", "cleared",
    name="transaction_status",
)
investigation_status_enum = postgresql.ENUM(
    "open", "pending_approval", "resolved", "dismissed",
    name="investigation_status",
)
risk_level_enum = postgresql.ENUM("low", "medium", "high", "critical", name="risk_level")


def upgrade() -> None:
    bind = op.get_bind()
    transaction_status_enum.create(bind, checkfirst=True)
    investigation_status_enum.create(bind, checkfirst=True)
    risk_level_enum.create(bind, checkfirst=True)

    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_departments_organization_id", "departments", ["organization_id"])

    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vendors_organization_id", "vendors", ["organization_id"])

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_code", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("transaction_date", sa.Date, nullable=False),
        sa.Column("status", transaction_status_enum, nullable=False, server_default="normal"),
        sa.Column("risk_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_policy_violation", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_transactions_organization_id", "transactions", ["organization_id"])
    op.create_index("ix_transactions_department_id", "transactions", ["department_id"])
    op.create_index("ix_transactions_vendor_id", "transactions", ["vendor_id"])
    op.create_index("ix_transactions_transaction_date", "transactions", ["transaction_date"])

    op.create_table(
        "investigations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", investigation_status_enum, nullable=False, server_default="open"),
        sa.Column("risk_level", risk_level_enum, nullable=False, server_default="medium"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_investigations_organization_id", "investigations", ["organization_id"])
    op.create_index("ix_investigations_transaction_id", "investigations", ["transaction_id"])


def downgrade() -> None:
    op.drop_table("investigations")
    op.drop_table("transactions")
    op.drop_table("vendors")
    op.drop_table("departments")
    risk_level_enum.drop(op.get_bind(), checkfirst=True)
    investigation_status_enum.drop(op.get_bind(), checkfirst=True)
    transaction_status_enum.drop(op.get_bind(), checkfirst=True)
