import uuid

from sqlalchemy.orm import Session

from app.ai_agents.graph import build_audit_graph
from app.core.exceptions import ResourceNotFoundError
from app.domain.models.agent_run_log import AgentRunLog
from app.domain.models.investigation import Investigation, InvestigationStatus
from app.domain.models.transaction import Transaction, TransactionStatus
from app.repositories.agent_run_log_repository import AgentRunLogRepository
from app.schemas.agent import AgentPipelineResult


class AgentService:
    """
    Orchestrates a single pipeline run: builds the graph, invokes it,
    then persists everything the graph produced in one place - the
    Transaction's new status/risk_score, the Investigation's
    evidence/recommendation (if one was opened), and every agent's
    run log. Nodes themselves only mutate in-memory state (except
    InvestigationAgent, whose entire job is creating that one row).
    """

    def __init__(self, db: Session):
        self.db = db

    def run_pipeline_for_transaction(self, organization_id: uuid.UUID, transaction_id: uuid.UUID) -> AgentPipelineResult:
        transaction = self.db.get(Transaction, transaction_id)
        if transaction is None or transaction.organization_id != organization_id:
            raise ResourceNotFoundError("Transaction")

        graph = build_audit_graph(self.db)
        initial_state = {
            "organization_id": str(organization_id),
            "transaction_id": str(transaction_id),
            "logs": [],
        }
        final_state = graph.invoke(initial_state)

        # Persist the transaction's updated risk assessment.
        transaction.risk_score = final_state.get("risk_score", transaction.risk_score)
        if final_state.get("should_investigate"):
            transaction.status = TransactionStatus.VIOLATION if final_state.get("policy_violations") else TransactionStatus.FLAGGED
            transaction.is_policy_violation = bool(final_state.get("policy_violations"))
        self.db.commit()

        investigation_id = final_state.get("investigation_id")
        if investigation_id:
            investigation = self.db.get(Investigation, uuid.UUID(investigation_id))
            if investigation:
                investigation.evidence_json = final_state.get("evidence")
                investigation.recommendation = final_state.get("recommendation")
                investigation.status = InvestigationStatus.PENDING_APPROVAL
                self.db.commit()

        # Persist every agent's run log for full auditability.
        log_repo = AgentRunLogRepository(self.db)
        for entry in final_state.get("logs", []):
            log_repo.create(
                AgentRunLog(
                    organization_id=organization_id,
                    investigation_id=uuid.UUID(investigation_id) if investigation_id else None,
                    transaction_id=transaction_id,
                    agent_name=entry["agent_name"],
                    step_order=entry["step_order"],
                    input_summary=entry["input_summary"],
                    output_summary=entry["output_summary"],
                    reasoning=entry["reasoning"],
                    metadata_json=entry.get("metadata", {}),
                    used_llm=entry.get("used_llm", False),
                )
            )

        return AgentPipelineResult(
            transaction_id=str(transaction_id),
            risk_score=final_state.get("risk_score", 0),
            is_anomalous=final_state.get("is_anomalous", False),
            should_investigate=bool(final_state.get("should_investigate")),
            investigation_id=investigation_id,
            policy_violations=final_state.get("policy_violations", []),
            recommendation=final_state.get("recommendation"),
        )
