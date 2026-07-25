import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.agent_run_log import AgentRunLog


class AgentRunLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AgentRunLog) -> AgentRunLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_for_investigation(self, investigation_id: uuid.UUID) -> list[AgentRunLog]:
        stmt = (
            select(AgentRunLog)
            .where(AgentRunLog.investigation_id == investigation_id)
            .order_by(AgentRunLog.step_order.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_recent_for_org(self, organization_id: uuid.UUID, limit: int = 20) -> list[AgentRunLog]:
        stmt = (
            select(AgentRunLog)
            .where(AgentRunLog.organization_id == organization_id)
            .order_by(AgentRunLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
