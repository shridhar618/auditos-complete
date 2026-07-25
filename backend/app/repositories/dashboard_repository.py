import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.domain.models.audit_log import AuditLog
from app.domain.models.investigation import Investigation, InvestigationStatus
from app.domain.models.lookup import Department, Vendor
from app.domain.models.transaction import Transaction, TransactionStatus
from app.domain.models.user import User


class DashboardRepository:
    """
    Encapsulates every aggregation query the dashboard needs. Kept
    separate from TransactionRepository/InvestigationRepository (which
    will arrive in their own CRUD-focused phases) because these are
    read-only, reporting-shaped queries rather than entity CRUD.
    """

    def __init__(self, db: Session):
        self.db = db

    def count_transactions(self, organization_id: uuid.UUID) -> int:
        stmt = select(func.count(Transaction.id)).where(Transaction.organization_id == organization_id)
        return self.db.execute(stmt).scalar_one()

    def count_critical_violations(self, organization_id: uuid.UUID) -> int:
        stmt = select(func.count(Transaction.id)).where(
            Transaction.organization_id == organization_id,
            Transaction.status == TransactionStatus.VIOLATION,
        )
        return self.db.execute(stmt).scalar_one()

    def average_risk_score(self, organization_id: uuid.UUID) -> float:
        stmt = select(func.coalesce(func.avg(Transaction.risk_score), 0)).where(
            Transaction.organization_id == organization_id
        )
        return float(self.db.execute(stmt).scalar_one())

    def count_investigations_by_status(self, organization_id: uuid.UUID, status: InvestigationStatus) -> int:
        stmt = select(func.count(Investigation.id)).where(
            Investigation.organization_id == organization_id, Investigation.status == status
        )
        return self.db.execute(stmt).scalar_one()

    def monthly_trend(self, organization_id: uuid.UUID, months_back: int = 6) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=months_back * 31)).date()
        month_col = func.to_char(Transaction.transaction_date, "YYYY-MM").label("month")

        is_flagged = case(
            (Transaction.status.in_([TransactionStatus.FLAGGED, TransactionStatus.UNDER_INVESTIGATION]), 1),
            else_=0,
        )
        is_violation = case((Transaction.status == TransactionStatus.VIOLATION, 1), else_=0)

        stmt = (
            select(
                month_col,
                func.count(Transaction.id).label("total"),
                func.sum(is_flagged).label("flagged"),
                func.sum(is_violation).label("violations"),
            )
            .where(Transaction.organization_id == organization_id, Transaction.transaction_date >= cutoff)
            .group_by(month_col)
            .order_by(month_col)
        )
        rows = self.db.execute(stmt).all()
        return [
            {"month": r.month, "total_transactions": r.total, "flagged_transactions": r.flagged or 0, "violations": r.violations or 0}
            for r in rows
        ]

    def department_risk(self, organization_id: uuid.UUID) -> list[dict]:
        is_violation = case((Transaction.is_policy_violation.is_(True), 1), else_=0)
        stmt = (
            select(
                Department.name.label("department"),
                func.coalesce(func.avg(Transaction.risk_score), 0).label("avg_risk"),
                func.count(Transaction.id).label("txn_count"),
                func.sum(is_violation).label("violation_count"),
            )
            .join(Transaction, Transaction.department_id == Department.id)
            .where(Department.organization_id == organization_id)
            .group_by(Department.name)
            .order_by(func.coalesce(func.avg(Transaction.risk_score), 0).desc())
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "department": r.department,
                "avg_risk_score": round(float(r.avg_risk), 1),
                "transaction_count": r.txn_count,
                "violation_count": r.violation_count or 0,
            }
            for r in rows
        ]

    def vendor_risk(self, organization_id: uuid.UUID, limit: int = 8) -> list[dict]:
        stmt = (
            select(
                Vendor.name.label("vendor"),
                func.coalesce(func.avg(Transaction.risk_score), 0).label("avg_risk"),
                func.count(Transaction.id).label("txn_count"),
            )
            .join(Transaction, Transaction.vendor_id == Vendor.id)
            .where(Vendor.organization_id == organization_id)
            .group_by(Vendor.name)
            .order_by(func.coalesce(func.avg(Transaction.risk_score), 0).desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            {"vendor": r.vendor, "avg_risk_score": round(float(r.avg_risk), 1), "transaction_count": r.txn_count}
            for r in rows
        ]

    def recent_activity(self, organization_id: uuid.UUID, limit: int = 10) -> list[dict]:
        stmt = (
            select(AuditLog, User.full_name)
            .outerjoin(User, User.id == AuditLog.actor_user_id)
            .where(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "actor_name": actor_name,
                "created_at": log.created_at,
            }
            for log, actor_name in rows
        ]
