"""reporting & analytics: reports table

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24
"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

report_type_enum = postgresql.ENUM("audit", "risk", "compliance", "department", "vendor", name="report_type")
report_format_enum = postgresql.ENUM("pdf", "excel", "csv", name="report_format")


def upgrade() -> None:
    bind = op.get_bind()
    report_type_enum.create(bind, checkfirst=True)
    report_format_enum.create(bind, checkfirst=True)

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("report_type", report_type_enum, nullable=False),
        sa.Column("format", report_format_enum, nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("date_from", sa.String(10), nullable=True),
        sa.Column("date_to", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reports_organization_id", "reports", ["organization_id"])


def downgrade() -> None:
    op.drop_table("reports")
    report_format_enum.drop(op.get_bind(), checkfirst=True)
    report_type_enum.drop(op.get_bind(), checkfirst=True)
