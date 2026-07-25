"""document & policy center: documents, policy_chunks, pgvector extension

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-24
"""
import uuid

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

document_category_enum = postgresql.ENUM(
    "invoice", "purchase_order", "contract", "bank_statement", "email", "policy", "other",
    name="document_category",
)
document_status_enum = postgresql.ENUM("processing", "ready", "failed", name="document_status")

EMBEDDING_DIMENSIONS = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    bind = op.get_bind()
    document_category_enum.create(bind, checkfirst=True)
    document_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("category", document_category_enum, nullable=False),
        sa.Column("status", document_status_enum, nullable=False, server_default="processing"),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("extraction_method", sa.String(30), nullable=True),
        sa.Column("processing_error", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_organization_id", "documents", ["organization_id"])

    op.create_table(
        "policy_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSIONS), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_policy_chunks_organization_id", "policy_chunks", ["organization_id"])
    op.create_index("ix_policy_chunks_document_id", "policy_chunks", ["document_id"])
    # IVFFlat index for fast approximate cosine search once there's meaningful data volume.
    op.execute(
        "CREATE INDEX ix_policy_chunks_embedding ON policy_chunks "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_table("policy_chunks")
    op.drop_table("documents")
    document_status_enum.drop(op.get_bind(), checkfirst=True)
    document_category_enum.drop(op.get_bind(), checkfirst=True)
