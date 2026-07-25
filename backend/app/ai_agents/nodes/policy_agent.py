"""
Policy Agent.

Checks the transaction against every active PolicyRule for the
organization. This is deliberately simple and deterministic (threshold
checks) - full semantic policy search over uploaded regulation/policy
documents (RBI, SOX, GST, internal PDFs) is the Document & Policy
Center phase, which will extend `policy_violations` with citations.
"""
import uuid

from sqlalchemy.orm import Session

from app.ai_agents.state import AuditState
from app.domain.models.policy_rule import PolicyRule, PolicyRuleType
from app.domain.models.transaction import Transaction
from app.repositories.policy_rule_repository import PolicyRuleRepository
from app.services.policy_document_service import PolicyDocumentService


class PolicyAgent:
    def __init__(self, db: Session):
        self.db = db
        self.rules = PolicyRuleRepository(db)
        self.policy_documents = PolicyDocumentService(db)

    def __call__(self, state: AuditState) -> AuditState:
        transaction = self.db.get(Transaction, uuid.UUID(state["transaction_id"]))
        logs = state.get("logs", [])

        if transaction is None:
            return {**state, "policy_violations": [], "policy_citations": [], "should_investigate": bool(state.get("is_anomalous")), "logs": logs}

        active_rules = self.rules.list_active_for_org(transaction.organization_id)
        violations = [
            self._describe_violation(rule, transaction)
            for rule in active_rules
            if self._is_violated(rule, transaction)
        ]

        # Also surface any relevant uploaded policy/regulation text (semantic if
        # available, keyword fallback otherwise) - informational citations, not
        # hard violations, since we can't assert a match is a rule breach without
        # a human reading the source document.
        search_query = transaction.description or f"transaction amount {transaction.amount}"
        citations = self.policy_documents.search(transaction.organization_id, search_query, top_k=3)

        should_investigate = bool(state.get("is_anomalous")) or len(violations) > 0

        logs.append(
            {
                "agent_name": "policy",
                "step_order": 2,
                "input_summary": f"Checked against {len(active_rules)} active policy rule(s); searched policy documents for '{search_query[:60]}'",
                "output_summary": f"{len(violations)} violation(s), {len(citations)} document citation(s) found",
                "reasoning": (
                    ("; ".join(v["description"] for v in violations) + ". " if violations else "No active policy rule was violated. ")
                    + (f"Found {len(citations)} potentially relevant policy document excerpt(s) for human review." if citations else "No relevant policy documents found.")
                ),
                "metadata": {"rule_count": len(active_rules), "citation_count": len(citations)},
                "used_llm": False,
            }
        )

        return {
            **state,
            "policy_violations": violations,
            "policy_citations": citations,
            "should_investigate": should_investigate,
            "logs": logs,
        }

    @staticmethod
    def _is_violated(rule: PolicyRule, transaction: Transaction) -> bool:
        if rule.threshold_amount is None:
            return False
        if rule.rule_type == PolicyRuleType.AMOUNT_THRESHOLD:
            return float(transaction.amount) > float(rule.threshold_amount)
        if rule.rule_type == PolicyRuleType.DEPARTMENT_THRESHOLD:
            return (
                rule.department_id is not None
                and transaction.department_id == rule.department_id
                and float(transaction.amount) > float(rule.threshold_amount)
            )
        return False

    @staticmethod
    def _describe_violation(rule: PolicyRule, transaction: Transaction) -> dict:
        return {
            "rule_id": str(rule.id),
            "rule_name": rule.name,
            "description": (
                f"'{rule.name}': {transaction.currency} {float(transaction.amount):,.2f} exceeds the "
                f"threshold of {float(rule.threshold_amount):,.2f}"
            ),
        }
