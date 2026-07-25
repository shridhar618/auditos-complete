import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.domain.models.investigation import InvestigationStatus, RiskLevel
from app.schemas.agent import AgentRunLogResponse


class InvestigationResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID | None
    transaction_reference: str | None = None
    status: InvestigationStatus
    risk_level: RiskLevel
    summary: str | None
    recommendation: str | None
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class InvestigationDetailResponse(InvestigationResponse):
    evidence_json: dict[str, Any] | None
    resolution_notes: str | None
    agent_logs: list[AgentRunLogResponse] = []


class InvestigationListResponse(BaseModel):
    items: list[InvestigationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ResolveInvestigationRequest(BaseModel):
    resolution_notes: str | None = None


class DismissInvestigationRequest(BaseModel):
    resolution_notes: str | None = None
