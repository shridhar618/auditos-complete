import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class DocumentCategory(str, enum.Enum):
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    CONTRACT = "contract"
    BANK_STATEMENT = "bank_statement"
    EMAIL = "email"
    POLICY = "policy"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    An uploaded file plus its extracted text. `category=POLICY` documents
    additionally get chunked and embedded into `PolicyChunk` rows so the
    Policy Agent and the Policy Center's search box can find them
    semantically. Every other category is searchable/previewable via
    `extracted_text` but is not embedded (that's Document Center scope,
    not Policy Center).
    """
    __tablename__ = "documents"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str] = mapped_column(String(150), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    category: Mapped[DocumentCategory] = mapped_column(Enum(DocumentCategory, name="document_category", values_callable=enum_values), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", values_callable=enum_values), nullable=False, default=DocumentStatus.PROCESSING
    )
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(30), nullable=True)  # "native", "ocr", "unsupported"
    processing_error: Mapped[str] = mapped_column(String(500), nullable=True)
