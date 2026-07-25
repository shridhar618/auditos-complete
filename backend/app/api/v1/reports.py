import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.user import User
from app.schemas.report import GenerateReportRequest, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=list[ReportResponse], dependencies=[Depends(require_permission("reports:read"))])
def list_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReportService(db).list_reports(current_user.organization_id)


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("reports:generate"))],
)
def generate_report(
    payload: GenerateReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ReportService(db).generate(
        organization_id=current_user.organization_id,
        generated_by_user_id=current_user.id,
        report_type=payload.report_type,
        report_format=payload.format,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )


@router.get("/{report_id}/download", dependencies=[Depends(require_permission("reports:read"))])
def download_report(report_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report, media_type = ReportService(db).get_report_for_download(current_user.organization_id, report_id)
    filename = f"{report.title.replace(' ', '_')}.{report.storage_path.rsplit('.', 1)[-1]}"
    return FileResponse(path=report.storage_path, media_type=media_type, filename=filename)
