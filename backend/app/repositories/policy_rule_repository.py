import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.policy_rule import PolicyRule


class PolicyRuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active_for_org(self, organization_id: uuid.UUID) -> list[PolicyRule]:
        stmt = select(PolicyRule).where(
            PolicyRule.organization_id == organization_id, PolicyRule.is_active.is_(True)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(self, rule: PolicyRule) -> PolicyRule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
