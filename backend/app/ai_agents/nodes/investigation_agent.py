"""
Investigation Agent.

Opens the actual Investigation record - the durable, human-visible
case a compliance officer or auditor will review. This is the one
node in the pipeline that creates the case itself; every later node
(Evidence, Recommendation) attaches more detail to it, and a human
must explicitly approve or dismiss it later (see InvestigationService).
"""
import uuid

from sqlalchemy.orm import Session

from app.ai_agents.state import AuditState
from app.domain.models.investigation import Investigation, InvestigationStatus, RiskLevel
from app.domain.models.transaction import Transaction


def _risk_level_for_score(risk_score: int) -> RiskLevel:
    if risk_score >= 85:
        return RiskLevel.CRITICAL
    if risk_score >= 65:
        return RiskLevel.HIGH
    if risk_score >= 40:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


class InvestigationAgent:
    def __init__(self, db: Session):
        self.db = db

    def __call__(self, state: AuditState) -> AuditState:
        logs = state.get("logs", [])
        transaction = self.db.get(Transaction, uuid.UUID(state["transaction_id"]))
        risk_score = state.get("risk_score", 0)
        risk_level = _risk_level_for_score(risk_score)

        investigation = Investigation(
            organization_id=uuid.UUID(state["organization_id"]),
            transaction_id=transaction.id if transaction else None,
            status=InvestigationStatus.OPEN,
            risk_level=risk_level,
            summary=(
                f"Opened automatically by the Detection/Policy Agents. "
                f"Risk score {risk_score}/100, {len(state.get('policy_violations', []))} policy violation(s) found."
            ),
        )
        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)

        logs.append(
            {
                "agent_name": "investigation",
                "step_order": 3,
                "input_summary": f"risk_score={risk_score}, policy_violations={len(state.get('policy_violations', []))}",
                "output_summary": f"Opened investigation {investigation.id} (risk_level={risk_level.value})",
                "reasoning": "Investigation opened because the transaction was statistically anomalous and/or violated an active policy rule.",
                "metadata": {"risk_level": risk_level.value},
                "used_llm": False,
            }
        )

        return {**state, "investigation_id": str(investigation.id), "risk_level": risk_level.value, "logs": logs}
