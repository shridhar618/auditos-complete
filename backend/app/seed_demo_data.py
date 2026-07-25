"""
Generates realistic sample transactions, departments, vendors, and
investigations for ONE organization, so the Dashboard module has real
rows to aggregate instead of an empty state.

This is a development/demo utility, not part of the production AI
pipeline - real transactions will eventually flow in via the
Transaction Management module and get scored by the Detection Agent.

Usage:
    python -m app.seed_demo_data --org-slug your-org-slug
"""
import argparse
import random
import uuid
from datetime import date, datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.domain.models.audit_log import AuditLog
from app.domain.models.investigation import Investigation, InvestigationStatus, RiskLevel
from app.domain.models.lookup import Department, Vendor
from app.domain.models.organization import Organization
from app.domain.models.policy_rule import PolicyRule, PolicyRuleType
from app.domain.models.transaction import Transaction, TransactionStatus
from app.domain.models.user import User

DEPARTMENT_NAMES = ["Procurement", "Finance", "Sales", "IT", "Human Resources", "Operations"]
VENDOR_NAMES = [
    "Global Supply Co", "Northbridge Logistics", "Apex Materials", "Union Freight",
    "Sterling Consulting", "Delta Hardware", "Vertex Cloud Services", "Harbor Print & Media",
]

ACTIONS = ["user.login", "transaction.flagged", "investigation.opened", "investigation.resolved", "policy.updated"]


def _random_status(risk_score: int) -> tuple[TransactionStatus, bool]:
    if risk_score >= 85:
        return TransactionStatus.VIOLATION, True
    if risk_score >= 65:
        return random.choice([TransactionStatus.FLAGGED, TransactionStatus.UNDER_INVESTIGATION]), random.random() < 0.3
    return TransactionStatus.NORMAL, False


def seed_demo_data(org_slug: str, transaction_count: int = 400) -> None:
    db = SessionLocal()
    try:
        organization = db.query(Organization).filter(Organization.slug == org_slug).one_or_none()
        if organization is None:
            raise SystemExit(f"No organization found with slug '{org_slug}'. Register an org first.")

        departments = [Department(organization_id=organization.id, name=name) for name in DEPARTMENT_NAMES]
        vendors = [Vendor(organization_id=organization.id, name=name) for name in VENDOR_NAMES]
        db.add_all(departments + vendors)
        db.flush()

        procurement = next((d for d in departments if d.name == "Procurement"), None)
        policy_rules = [
            PolicyRule(
                organization_id=organization.id,
                name="Large Purchase Threshold",
                description="Any single transaction over $75,000 requires manual review.",
                rule_type=PolicyRuleType.AMOUNT_THRESHOLD,
                threshold_amount=75_000,
            ),
        ]
        if procurement:
            policy_rules.append(
                PolicyRule(
                    organization_id=organization.id,
                    department_id=procurement.id,
                    name="Procurement Approval Limit",
                    description="Procurement transactions over $30,000 require a second approver.",
                    rule_type=PolicyRuleType.DEPARTMENT_THRESHOLD,
                    threshold_amount=30_000,
                )
            )
        db.add_all(policy_rules)
        db.flush()

        today = date.today()
        transactions: list[Transaction] = []
        for i in range(transaction_count):
            days_ago = random.randint(0, 180)
            txn_date = today - timedelta(days=days_ago)
            risk_score = min(100, max(0, int(random.gauss(30, 25))))
            status, is_violation = _random_status(risk_score)

            transactions.append(
                Transaction(
                    organization_id=organization.id,
                    department_id=random.choice(departments).id,
                    vendor_id=random.choice(vendors).id,
                    reference_code=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                    description=f"Sample transaction #{i + 1} generated for demo purposes",
                    amount=round(random.uniform(150, 250_000), 2),
                    currency="USD",
                    transaction_date=txn_date,
                    status=status,
                    risk_score=risk_score,
                    is_policy_violation=is_violation,
                )
            )
        db.add_all(transactions)
        db.flush()

        flagged_transactions = [t for t in transactions if t.status in (TransactionStatus.FLAGGED, TransactionStatus.UNDER_INVESTIGATION, TransactionStatus.VIOLATION)]
        admin_user = db.query(User).filter(User.organization_id == organization.id).first()

        investigations = []
        for txn in random.sample(flagged_transactions, k=min(len(flagged_transactions), 60)):
            opened_days_ago = random.randint(0, 60)
            is_resolved = random.random() < 0.55
            investigations.append(
                Investigation(
                    organization_id=organization.id,
                    transaction_id=txn.id,
                    assigned_to_user_id=admin_user.id if admin_user else None,
                    status=InvestigationStatus.RESOLVED if is_resolved else random.choice(
                        [InvestigationStatus.OPEN, InvestigationStatus.PENDING_APPROVAL]
                    ),
                    risk_level=RiskLevel.CRITICAL if txn.risk_score >= 85 else RiskLevel.HIGH if txn.risk_score >= 65 else RiskLevel.MEDIUM,
                    summary=f"Investigation into {txn.reference_code} (risk score {txn.risk_score})",
                    resolved_at=(datetime.now(timezone.utc) - timedelta(days=opened_days_ago // 2)) if is_resolved else None,
                )
            )
        db.add_all(investigations)

        activity_logs = []
        for i in range(20):
            hours_ago = random.randint(1, 24 * 14)
            activity_logs.append(
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=admin_user.id if admin_user else None,
                    action=random.choice(ACTIONS),
                    resource_type="Transaction",
                    resource_id=str(random.choice(transactions).id),
                    metadata_json={"seeded": True},
                    ip_address="203.0.113.10",
                )
            )
            activity_logs[-1].created_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        db.add_all(activity_logs)

        db.commit()
        print(
            f"Seeded {len(transactions)} transactions, {len(investigations)} investigations, "
            f"{len(departments)} departments, {len(vendors)} vendors, {len(policy_rules)} policy rules, "
            f"{len(activity_logs)} activity logs for organization '{org_slug}'."
        )
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo data for the AuditOS dashboard.")
    parser.add_argument("--org-slug", required=True, help="Slug of the organization to seed (see /auth/register response or DB).")
    parser.add_argument("--count", type=int, default=400, help="Number of demo transactions to generate.")
    args = parser.parse_args()
    seed_demo_data(args.org_slug, args.count)
