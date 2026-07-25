import uuid

from sqlalchemy.orm import Session

from app.domain.models.investigation import InvestigationStatus
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DepartmentRisk,
    KPISummary,
    MonthlyTrendPoint,
    RecentActivityItem,
    VendorRisk,
)


class DashboardService:
    """
    Turns raw aggregates into the KPIs the UI actually needs.

    Compliance score is intentionally the inverse of average risk,
    penalized further by the proportion of transactions that are
    outright violations - a portfolio with a few low-risk flags looks
    very different from one with the same average risk driven by a
    handful of severe violations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = DashboardRepository(db)

    def get_summary(self, organization_id: uuid.UUID) -> DashboardSummaryResponse:
        total_transactions = self.repo.count_transactions(organization_id)
        avg_risk = self.repo.average_risk_score(organization_id)
        critical_violations = self.repo.count_critical_violations(organization_id)

        violation_ratio = (critical_violations / total_transactions) if total_transactions else 0.0
        compliance_score = max(0.0, 100.0 - avg_risk - (violation_ratio * 100 * 0.5))

        kpis = KPISummary(
            compliance_score=round(compliance_score, 1),
            risk_score=round(avg_risk, 1),
            critical_violations=critical_violations,
            pending_investigations=self.repo.count_investigations_by_status(organization_id, InvestigationStatus.OPEN)
            + self.repo.count_investigations_by_status(organization_id, InvestigationStatus.PENDING_APPROVAL),
            open_cases=self.repo.count_investigations_by_status(organization_id, InvestigationStatus.OPEN),
            resolved_cases=self.repo.count_investigations_by_status(organization_id, InvestigationStatus.RESOLVED),
            total_transactions=total_transactions,
        )

        return DashboardSummaryResponse(
            kpis=kpis,
            monthly_trend=[MonthlyTrendPoint(**row) for row in self.repo.monthly_trend(organization_id)],
            department_risk=[DepartmentRisk(**row) for row in self.repo.department_risk(organization_id)],
            vendor_risk=[VendorRisk(**row) for row in self.repo.vendor_risk(organization_id)],
            recent_activity=[RecentActivityItem(**row) for row in self.repo.recent_activity(organization_id)],
        )
