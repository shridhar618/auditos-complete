import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class ReportType(str, enum.Enum):
    AUDIT = "audit"
    RISK = "risk"
    COMPLIANCE = "compliance"
    DEPARTMENT = "department"
    VENDOR = "vendor"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A generated, downloadable report. Generation logic lives in
    ReportGenerationService and reuses the same aggregation queries as
    the Dashboard module (DashboardRepository) rather than duplicating
    them - this table just tracks what was produced, by whom, and where
    the file lives, so it can be re-downloaded without regenerating it.
    """
    __tablename__ = "reports"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType, name="report_type", values_callable=enum_values), nullable=False)
    format: Mapped[ReportFormat] = mapped_column(Enum(ReportFormat, name="report_format", values_callable=enum_values), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    date_from: Mapped[str] = mapped_column(String(10), nullable=True)  # ISO date, kept as string for simple display
    date_to: Mapped[str] = mapped_column(String(10), nullable=True)
