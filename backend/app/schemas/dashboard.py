from datetime import datetime

from pydantic import BaseModel


class KPISummary(BaseModel):
    compliance_score: float          # 0-100, higher is better
    risk_score: float                # 0-100, higher is worse
    critical_violations: int
    pending_investigations: int
    open_cases: int
    resolved_cases: int
    total_transactions: int


class MonthlyTrendPoint(BaseModel):
    month: str                       # "2026-01"
    total_transactions: int
    flagged_transactions: int
    violations: int


class DepartmentRisk(BaseModel):
    department: str
    avg_risk_score: float
    transaction_count: int
    violation_count: int


class VendorRisk(BaseModel):
    vendor: str
    avg_risk_score: float
    transaction_count: int


class RecentActivityItem(BaseModel):
    action: str
    resource_type: str
    resource_id: str | None
    actor_name: str | None
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    kpis: KPISummary
    monthly_trend: list[MonthlyTrendPoint]
    department_risk: list[DepartmentRisk]
    vendor_risk: list[VendorRisk]
    recent_activity: list[RecentActivityItem]
