import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.domain.models.report import ReportFormat, ReportType


class GenerateReportRequest(BaseModel):
    report_type: ReportType
    format: ReportFormat
    date_from: date | None = None
    date_to: date | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    report_type: ReportType
    format: ReportFormat
    file_size_bytes: int
    date_from: str | None
    date_to: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
