from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgentPipelineResult(BaseModel):
    transaction_id: str
    risk_score: int
    is_anomalous: bool
    should_investigate: bool
    investigation_id: str | None
    policy_violations: list[dict[str, Any]]
    recommendation: str | None


class AgentRunLogResponse(BaseModel):
    agent_name: str
    step_order: int
    input_summary: str | None
    output_summary: str | None
    reasoning: str | None
    metadata_json: dict[str, Any] | None
    used_llm: bool
    created_at: datetime

    model_config = {"from_attributes": True}
