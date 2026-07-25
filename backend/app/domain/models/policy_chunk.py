import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PolicyChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    One chunk of a policy document's text, plus its embedding vector.
    `embedding` is nullable: if no OPENAI_API_KEY is configured at
    upload time, chunks are stored without embeddings and the Policy
    Center falls back to keyword search over `chunk_text` instead of
    fabricating a similarity score.
    """
    __tablename__ = "policy_chunks"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=True)
