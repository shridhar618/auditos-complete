"""
Evidence Agent.

Assembles the structured evidence bundle a human reviewer sees when
opening the case: the transaction snapshot, the specific policy rules
that were violated, and the statistical basis for the risk score.
Once the Document Center exists, this is where matched source
documents (invoices, contracts, emails) would be attached too.
"""
import uuid

from sqlalchemy.orm import Session

from app.ai_agents.state import AuditState
from app.domain.models.transaction import Transaction


class EvidenceAgent:
    def __init__(self, db: Session):
        self.db = db

    def __call__(self, state: AuditState) -> AuditState:
        logs = state.get("logs", [])
        transaction = self.db.get(Transaction, uuid.UUID(state["transaction_id"]))

        evidence = {
            "transaction_snapshot": {
                "reference_code": transaction.reference_code if transaction else None,
                "amount": float(transaction.amount) if transaction else None,
                "currency": transaction.currency if transaction else None,
                "transaction_date": transaction.transaction_date.isoformat() if transaction else None,
            },
            "risk_score": state.get("risk_score"),
            "detection_reasoning": state.get("detection_reasoning"),
            "policy_violations": state.get("policy_violations", []),
            "policy_citations": state.get("policy_citations", []),
        }

        logs.append(
            {
                "agent_name": "evidence",
                "step_order": 4,
                "input_summary": f"investigation_id={state.get('investigation_id')}",
                "output_summary": f"Assembled evidence bundle with {len(evidence['policy_violations'])} policy violation(s)",
                "reasoning": "Evidence bundle combines the transaction snapshot, detection statistics, and matched policy rules for human review.",
                "metadata": {},
                "used_llm": False,
            }
        )

        return {**state, "evidence": evidence, "logs": logs}
