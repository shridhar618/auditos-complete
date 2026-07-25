import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.report import Report


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_for_org(self, organization_id: uuid.UUID) -> list[Report]:
        stmt = select(Report).where(Report.organization_id == organization_id).order_by(Report.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, organization_id: uuid.UUID, report_id: uuid.UUID) -> Report | None:
        stmt = select(Report).where(Report.organization_id == organization_id, Report.id == report_id)
        return self.db.execute(stmt).scalar_one_or_none()
