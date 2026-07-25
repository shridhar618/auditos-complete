import uuid
from datetime import date, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.domain.models.investigation import Investigation
from app.domain.models.lookup import Department
from app.domain.models.transaction import Transaction

RISK_BANDS = [
    ("low", 0, 39),
    ("medium", 40, 64),
    ("high", 65, 84),
    ("critical", 85, 100),
]


class AnalyticsRepository:
    """
    Deeper cross-cutting aggregations that don't belong on the
    Dashboard (which stays high-level KPIs) but power the Analytics
    page's heatmap and timeline views. Reuses the same Transaction/
    Investigation tables the Dashboard and AI pipeline already write to.
    """

    def __init__(self, db: Session):
        self.db = db

    def risk_matrix(self, organization_id: uuid.UUID) -> list[dict]:
        """Department x risk-band transaction counts - the data behind a heatmap grid."""
        band_case = case(
            *[
                (Transaction.risk_score.between(lo, hi), label)
                for label, lo, hi in RISK_BANDS
            ],
            else_="low",
        ).label("risk_band")

        stmt = (
            select(Department.name.label("department"), band_case, func.count(Transaction.id).label("count"))
            .join(Transaction, Transaction.department_id == Department.id)
            .where(Department.organization_id == organization_id)
            .group_by(Department.name, band_case)
        )
        rows = self.db.execute(stmt).all()
        return [{"department": r.department, "risk_band": r.risk_band, "count": r.count} for r in rows]

    def investigation_timeline(self, organization_id: uuid.UUID, weeks_back: int = 12) -> list[dict]:
        """Investigations opened per week, broken down by current status."""
        cutoff = date.today() - timedelta(weeks=weeks_back)
        week_col = func.to_char(Investigation.created_at, "IYYY-IW").label("week")

        stmt = (
            select(
                week_col,
                func.count(Investigation.id).label("total"),
                func.sum(case((Investigation.status == "resolved", 1), else_=0)).label("resolved"),
                func.sum(case((Investigation.status == "dismissed", 1), else_=0)).label("dismissed"),
                func.sum(
                    case((Investigation.status.in_(["open", "pending_approval"]), 1), else_=0)
                ).label("pending"),
            )
            .where(Investigation.organization_id == organization_id, Investigation.created_at >= cutoff)
            .group_by(week_col)
            .order_by(week_col)
        )
        rows = self.db.execute(stmt).all()
        return [
            {"week": r.week, "total": r.total, "resolved": r.resolved or 0, "dismissed": r.dismissed or 0, "pending": r.pending or 0}
            for r in rows
        ]

    def reviewer_activity(self, organization_id: uuid.UUID) -> list[dict]:
        """Cases resolved/dismissed per reviewer - a simple accountability view."""
        from app.domain.models.user import User

        stmt = (
            select(
                User.full_name,
                func.count(Investigation.id).label("total_decided"),
                func.sum(case((Investigation.status == "resolved", 1), else_=0)).label("resolved"),
                func.sum(case((Investigation.status == "dismissed", 1), else_=0)).label("dismissed"),
            )
            .join(User, Investigation.approved_by_user_id == User.id)
            .where(Investigation.organization_id == organization_id)
            .group_by(User.full_name)
            .order_by(func.count(Investigation.id).desc())
        )
        rows = self.db.execute(stmt).all()
        return [
            {"reviewer_name": r.full_name, "total_decided": r.total_decided, "resolved": r.resolved or 0, "dismissed": r.dismissed or 0}
            for r in rows
        ]
