import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.user import User
from app.repositories.agent_run_log_repository import AgentRunLogRepository
from app.schemas.agent import AgentPipelineResult, AgentRunLogResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.post(
    "/run/{transaction_id}",
    response_model=AgentPipelineResult,
    dependencies=[Depends(require_permission("investigations:write"))],
)
def run_pipeline(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Runs Detection -> Policy -> (Investigation -> Evidence -> Recommendation) for one transaction."""
    return AgentService(db).run_pipeline_for_transaction(current_user.organization_id, transaction_id)


@router.get(
    "/runs/recent",
    response_model=list[AgentRunLogResponse],
    dependencies=[Depends(require_permission("investigations:read"))],
)
def recent_agent_runs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Recent agent activity across the organization - powers the AI Agents observability page."""
    logs = AgentRunLogRepository(db).list_recent_for_org(current_user.organization_id)
    return [AgentRunLogResponse.model_validate(log) for log in logs]
