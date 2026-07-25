"""
The shared state object threaded through every node in the audit
pipeline graph. Each agent reads what it needs and appends to
`logs` - the full list becomes the auditable trail persisted to
AgentRunLog after the graph finishes.
"""
from typing import Any, TypedDict


class AgentLogEntry(TypedDict):
    agent_name: str
    step_order: int
    input_summary: str
    output_summary: str
    reasoning: str
    metadata: dict[str, Any]
    used_llm: bool


class AuditState(TypedDict, total=False):
    # identifiers
    organization_id: str
    transaction_id: str

    # populated by DetectionAgent
    risk_score: int
    is_anomalous: bool
    detection_reasoning: str

    # populated by PolicyAgent
    policy_violations: list[dict[str, Any]]
    policy_citations: list[dict[str, Any]]

    # populated by InvestigationAgent
    investigation_id: str
    risk_level: str

    # populated by EvidenceAgent
    evidence: dict[str, Any]

    # populated by RecommendationAgent
    recommendation: str

    # accumulated by every node
    logs: list[AgentLogEntry]

    # control flow
    should_investigate: bool
