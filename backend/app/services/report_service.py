import os
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundError
from app.domain.models.report import Report, ReportFormat, ReportType
from app.repositories.report_repository import ReportRepository
from app.services import report_data_builder, report_renderers

_RENDERERS = {
    ReportFormat.PDF: (report_renderers.render_pdf, "pdf", "application/pdf"),
    ReportFormat.EXCEL: (report_renderers.render_excel, "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ReportFormat.CSV: (report_renderers.render_csv, "csv", "text/csv"),
}


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportRepository(db)

    def generate(
        self,
        organization_id: uuid.UUID,
        generated_by_user_id: uuid.UUID,
        report_type: ReportType,
        report_format: ReportFormat,
        date_from: date | None,
        date_to: date | None,
    ) -> Report:
        data = report_data_builder.build_report_data(self.db, organization_id, report_type, date_from, date_to)
        render_fn, extension, _ = _RENDERERS[report_format]
        file_bytes = render_fn(data)

        org_dir = os.path.join(settings.UPLOAD_DIR, str(organization_id), "reports")
        os.makedirs(org_dir, exist_ok=True)
        filename = f"{report_type.value}_{uuid.uuid4().hex[:8]}.{extension}"
        full_path = os.path.join(org_dir, filename)
        with open(full_path, "wb") as f:
            f.write(file_bytes)

        report = Report(
            organization_id=organization_id,
            generated_by_user_id=generated_by_user_id,
            title=data.title,
            report_type=report_type,
            format=report_format,
            storage_path=full_path,
            file_size_bytes=len(file_bytes),
            date_from=date_from.isoformat() if date_from else None,
            date_to=date_to.isoformat() if date_to else None,
        )
        return self.repo.create(report)

    def list_reports(self, organization_id: uuid.UUID) -> list[Report]:
        return self.repo.list_for_org(organization_id)

    def get_report_for_download(self, organization_id: uuid.UUID, report_id: uuid.UUID) -> tuple[Report, str]:
        report = self.repo.get_by_id(organization_id, report_id)
        if report is None or not os.path.exists(report.storage_path):
            raise ResourceNotFoundError("Report")
        _, _, media_type = _RENDERERS[report.format]
        return report, media_type
