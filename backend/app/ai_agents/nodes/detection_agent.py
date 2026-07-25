"""
Detection Agent.

Computes a 0-100 risk score for a transaction using real statistics
(z-score of the amount against its peer group's historical mean/stddev),
NOT a random or hardcoded number. An LLM is only ever used to phrase the
*explanation* of an already-computed score - the score itself stays
fully deterministic and reproducible, which matters for an audit trail.
"""
import statistics
import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_agents.llm_client import generate_explanation
from app.ai_agents.state import AuditState
from app.domain.models.transaction import Transaction

RISK_FLAG_THRESHOLD = 60
LOOKBACK_DAYS = 180
MIN_PEER_GROUP_SIZE = 5
LARGE_AMOUNT_THRESHOLD = 100_000


class DetectionAgent:
    def __init__(self, db: Session):
        self.db = db

    def __call__(self, state: AuditState) -> AuditState:
        transaction = self.db.get(Transaction, uuid.UUID(state["transaction_id"]))
        logs = state.get("logs", [])

        if transaction is None:
            logs.append(
                {
                    "agent_name": "detection",
                    "step_order": 1,
                    "input_summary": f"transaction_id={state['transaction_id']}",
                    "output_summary": "Transaction not found",
                    "reasoning": "Aborted - transaction no longer exists.",
                    "metadata": {},
                    "used_llm": False,
                }
            )
            return {**state, "risk_score": 0, "is_anomalous": False, "logs": logs}

        peers = self._get_peer_amounts(transaction)
        z_score, peer_count = self._compute_z_score(float(transaction.amount), peers)

        risk_score = 50 + (z_score * 15)
        if float(transaction.amount) >= LARGE_AMOUNT_THRESHOLD:
            risk_score += 10
        risk_score = int(min(100, max(0, round(risk_score))))
        is_anomalous = risk_score >= RISK_FLAG_THRESHOLD

        template_reasoning = (
            f"Amount {transaction.currency} {float(transaction.amount):,.2f} compared against "
            f"{peer_count} peer transaction(s) from the last {LOOKBACK_DAYS} days "
            f"(z-score: {z_score:+.2f}). "
            + ("Flagged as anomalous." if is_anomalous else "Within normal range.")
        )

        reasoning = template_reasoning
        used_llm = False
        llm_text = generate_explanation(
            system_prompt=(
                "You are a financial audit analyst. Explain, in 2 sentences, why a transaction's "
                "computed risk score is what it is, given the statistical inputs. Be precise and factual, "
                "do not invent facts not given to you."
            ),
            user_prompt=(
                f"Transaction amount: {transaction.currency} {float(transaction.amount):,.2f}. "
                f"Peer group size: {peer_count}. Z-score vs peer group: {z_score:+.2f}. "
                f"Computed risk score: {risk_score}/100. Flagged: {is_anomalous}."
            ),
        )
        if llm_text:
            reasoning = llm_text
            used_llm = True

        logs.append(
            {
                "agent_name": "detection",
                "step_order": 1,
                "input_summary": f"{transaction.reference_code}, amount={transaction.amount} {transaction.currency}, peer_group_size={peer_count}",
                "output_summary": f"risk_score={risk_score}, anomalous={is_anomalous}",
                "reasoning": reasoning,
                "metadata": {"z_score": round(z_score, 3), "peer_count": peer_count},
                "used_llm": used_llm,
            }
        )

        return {
            **state,
            "risk_score": risk_score,
            "is_anomalous": is_anomalous,
            "detection_reasoning": reasoning,
            "logs": logs,
        }

    def _get_peer_amounts(self, transaction: Transaction) -> list[float]:
        cutoff = date.today() - timedelta(days=LOOKBACK_DAYS)
        stmt = select(Transaction.amount).where(
            Transaction.organization_id == transaction.organization_id,
            Transaction.id != transaction.id,
            Transaction.transaction_date >= cutoff,
        )
        if transaction.department_id:
            stmt = stmt.where(Transaction.department_id == transaction.department_id)
        elif transaction.vendor_id:
            stmt = stmt.where(Transaction.vendor_id == transaction.vendor_id)

        return [float(a) for a in self.db.execute(stmt).scalars().all()]

    @staticmethod
    def _compute_z_score(amount: float, peers: list[float]) -> tuple[float, int]:
        if len(peers) < MIN_PEER_GROUP_SIZE:
            return 0.0, len(peers)
        mean = statistics.mean(peers)
        stdev = statistics.pstdev(peers)
        if stdev == 0:
            return 0.0, len(peers)
        return (amount - mean) / stdev, len(peers)
