"""
Recommendation Agent.

Produces the final, human-readable recommendation attached to the
case. Uses the LLM (if configured) to phrase a clear recommendation
grounded strictly in the evidence already gathered; otherwise falls
back to a deterministic template so the pipeline still produces a
useful, non-fabricated recommendation without an API key.

This is advisory only - the Recommendation Agent never changes the
investigation's status. A human always makes the final call.
"""
from app.ai_agents.llm_client import generate_explanation
from app.ai_agents.state import AuditState


class RecommendationAgent:
    def __call__(self, state: AuditState) -> AuditState:
        logs = state.get("logs", [])
        risk_score = state.get("risk_score", 0)
        violations = state.get("policy_violations", [])

        template = (
            f"This transaction was flagged with a risk score of {risk_score}/100. "
            + (
                f"It violates {len(violations)} active policy rule(s): "
                + "; ".join(v["rule_name"] for v in violations) + ". "
                if violations
                else "No specific policy rule was violated, but its amount is statistically unusual "
                "compared to similar transactions. "
            )
            + "Recommend a manual review of supporting documentation (invoice, PO, approval chain) "
            "before clearing or escalating this transaction."
        )

        recommendation = template
        used_llm = False
        llm_text = generate_explanation(
            system_prompt=(
                "You are a compliance recommendation assistant. Based only on the facts given, write a short, "
                "professional recommendation (2-3 sentences) for a human auditor reviewing this flagged transaction. "
                "Do not invent any facts not provided. End with a concrete next action."
            ),
            user_prompt=(
                f"Risk score: {risk_score}/100. Policy violations: "
                f"{[v['rule_name'] for v in violations] if violations else 'none'}. "
                f"Detection reasoning: {state.get('detection_reasoning', 'n/a')}"
            ),
        )
        if llm_text:
            recommendation = llm_text
            used_llm = True

        logs.append(
            {
                "agent_name": "recommendation",
                "step_order": 5,
                "input_summary": f"risk_score={risk_score}, violations={len(violations)}",
                "output_summary": recommendation[:200],
                "reasoning": "Recommendation is advisory only; investigation status is left as pending_approval for a human to decide.",
                "metadata": {},
                "used_llm": used_llm,
            }
        )

        return {**state, "recommendation": recommendation, "logs": logs}
