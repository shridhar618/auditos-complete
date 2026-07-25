"""
Import every model here so that Base.metadata is fully populated
before Alembic's autogenerate compares it against the database.
"""
from app.domain.models.organization import Organization  # noqa: F401
from app.domain.models.rbac import Permission, Role, role_permissions  # noqa: F401
from app.domain.models.user import User  # noqa: F401
from app.domain.models.refresh_token import RefreshToken  # noqa: F401
from app.domain.models.audit_log import AuditLog  # noqa: F401
from app.domain.models.lookup import Department, Vendor  # noqa: F401
from app.domain.models.transaction import Transaction, TransactionStatus  # noqa: F401
from app.domain.models.investigation import Investigation, InvestigationStatus, RiskLevel  # noqa: F401
from app.domain.models.policy_rule import PolicyRule, PolicyRuleType  # noqa: F401
from app.domain.models.agent_run_log import AgentRunLog  # noqa: F401
from app.domain.models.document import Document, DocumentCategory, DocumentStatus  # noqa: F401
from app.domain.models.policy_chunk import PolicyChunk  # noqa: F401
from app.domain.models.report import Report, ReportType, ReportFormat  # noqa: F401

__all__ = [
    "Organization",
    "Permission",
    "Role",
    "role_permissions",
    "User",
    "RefreshToken",
    "AuditLog",
    "Department",
    "Vendor",
    "Transaction",
    "TransactionStatus",
    "Investigation",
    "InvestigationStatus",
    "RiskLevel",
    "PolicyRule",
    "PolicyRuleType",
    "AgentRunLog",
    "Document",
    "DocumentCategory",
    "DocumentStatus",
    "PolicyChunk",
    "Report",
    "ReportType",
    "ReportFormat",
]
