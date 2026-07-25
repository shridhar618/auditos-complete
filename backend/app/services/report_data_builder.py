import uuid
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.domain.models.investigation import InvestigationStatus
from app.domain.models.report import ReportType
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.investigation_repository import InvestigationRepository


@dataclass
class ReportData:
    title: str
    subtitle: str
    kpis: list[tuple[str, str]] = field(default_factory=list)
    table_headers: list[str] = field(default_factory=list)
    table_rows: list[list[str]] = field(default_factory=list)


def build_report_data(
    db: Session,
    organization_id: uuid.UUID,
    report_type: ReportType,
    date_from: date | None,
    date_to: date | None,
) -> ReportData:
    dashboard_repo = DashboardRepository(db)
    subtitle = f"Period: {date_from or 'All time'} — {date_to or 'present'}"

    if report_type == ReportType.AUDIT:
        return _build_audit_report(db, organization_id, subtitle)
    if report_type == ReportType.RISK:
        return _build_risk_report(db, organization_id, dashboard_repo, subtitle)
    if report_type == ReportType.COMPLIANCE:
        return _build_compliance_report(db, organization_id, dashboard_repo, subtitle)
    if report_type == ReportType.DEPARTMENT:
        return _build_department_report(organization_id, dashboard_repo, subtitle)
    if report_type == ReportType.VENDOR:
        return _build_vendor_report(organization_id, dashboard_repo, subtitle)

    raise ValueError(f"Unknown report type: {report_type}")


def _build_audit_report(db: Session, organization_id: uuid.UUID, subtitle: str) -> ReportData:
    investigations, total = InvestigationRepository(db).list_for_org(organization_id, status=None, page=1, page_size=500)
    rows = [
        [
            inv.transaction.reference_code if inv.transaction else "—",
            inv.status.value,
            inv.risk_level.value,
            (inv.summary or "")[:120],
            inv.created_at.strftime("%Y-%m-%d"),
        ]
        for inv in investigations
    ]
    resolved = sum(1 for i in investigations if i.status == InvestigationStatus.RESOLVED)
    dismissed = sum(1 for i in investigations if i.status == InvestigationStatus.DISMISSED)
    return ReportData(
        title="Audit Investigation Report",
        subtitle=subtitle,
        kpis=[
            ("Total Cases", str(total)),
            ("Resolved", str(resolved)),
            ("Dismissed (False Positive)", str(dismissed)),
            ("Still Open", str(total - resolved - dismissed)),
        ],
        table_headers=["Transaction", "Status", "Risk Level", "Summary", "Opened"],
        table_rows=rows,
    )


def _build_risk_report(db: Session, organization_id: uuid.UUID, dashboard_repo: DashboardRepository, subtitle: str) -> ReportData:
    matrix = AnalyticsRepository(db).risk_matrix(organization_id)
    avg_risk = dashboard_repo.average_risk_score(organization_id)
    critical = dashboard_repo.count_critical_violations(organization_id)
    rows = [[m["department"], m["risk_band"], str(m["count"])] for m in matrix]
    return ReportData(
        title="Risk Assessment Report",
        subtitle=subtitle,
        kpis=[
            ("Average Risk Score", f"{avg_risk:.1f} / 100"),
            ("Critical Violations", str(critical)),
        ],
        table_headers=["Department", "Risk Band", "Transaction Count"],
        table_rows=rows,
    )


def _build_compliance_report(db: Session, organization_id: uuid.UUID, dashboard_repo: DashboardRepository, subtitle: str) -> ReportData:
    total = dashboard_repo.count_transactions(organization_id)
    avg_risk = dashboard_repo.average_risk_score(organization_id)
    critical = dashboard_repo.count_critical_violations(organization_id)
    violation_ratio = (critical / total) if total else 0.0
    compliance_score = max(0.0, 100.0 - avg_risk - (violation_ratio * 100 * 0.5))

    dept_rows = dashboard_repo.department_risk(organization_id)
    rows = [[d["department"], f"{d['avg_risk_score']:.1f}", str(d["transaction_count"]), str(d["violation_count"])] for d in dept_rows]
    return ReportData(
        title="Compliance Report",
        subtitle=subtitle,
        kpis=[
            ("Compliance Score", f"{compliance_score:.1f}%"),
            ("Total Transactions Reviewed", str(total)),
            ("Policy Violations", str(critical)),
        ],
        table_headers=["Department", "Avg Risk Score", "Transactions", "Violations"],
        table_rows=rows,
    )


def _build_department_report(organization_id: uuid.UUID, dashboard_repo: DashboardRepository, subtitle: str) -> ReportData:
    dept_rows = dashboard_repo.department_risk(organization_id)
    rows = [[d["department"], f"{d['avg_risk_score']:.1f}", str(d["transaction_count"]), str(d["violation_count"])] for d in dept_rows]
    return ReportData(
        title="Department Risk Report",
        subtitle=subtitle,
        kpis=[("Departments Analyzed", str(len(dept_rows)))],
        table_headers=["Department", "Avg Risk Score", "Transactions", "Violations"],
        table_rows=rows,
    )


def _build_vendor_report(organization_id: uuid.UUID, dashboard_repo: DashboardRepository, subtitle: str) -> ReportData:
    vendor_rows = dashboard_repo.vendor_risk(organization_id, limit=100)
    rows = [[v["vendor"], f"{v['avg_risk_score']:.1f}", str(v["transaction_count"])] for v in vendor_rows]
    return ReportData(
        title="Vendor Risk Report",
        subtitle=subtitle,
        kpis=[("Vendors Analyzed", str(len(vendor_rows)))],
        table_headers=["Vendor", "Avg Risk Score", "Transactions"],
        table_rows=rows,
    )
