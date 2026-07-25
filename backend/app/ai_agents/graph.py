"""
The Supervisor Agent, expressed as a LangGraph StateGraph.

Flow:

    Transaction
       |
    Detection Agent (statistical anomaly score)
       |
    Policy Agent (threshold rule checks)
       |
   [is_anomalous OR has policy_violations?] --no--> END (no case opened)
       |yes
    Investigation Agent (opens the case)
       |
    Evidence Agent (assembles the evidence bundle)
       |
    Recommendation Agent (advisory suggestion)
       |
      END  (investigation left at PENDING_APPROVAL - a human decides next)

A fresh graph is built per request, bound to that request's DB
session, so there is no shared mutable state between requests.
"""
from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.ai_agents.nodes.detection_agent import DetectionAgent
from app.ai_agents.nodes.evidence_agent import EvidenceAgent
from app.ai_agents.nodes.investigation_agent import InvestigationAgent
from app.ai_agents.nodes.policy_agent import PolicyAgent
from app.ai_agents.nodes.recommendation_agent import RecommendationAgent
from app.ai_agents.state import AuditState


def build_audit_graph(db: Session):
    graph = StateGraph(AuditState)

    graph.add_node("detection", DetectionAgent(db))
    graph.add_node("policy", PolicyAgent(db))
    graph.add_node("investigation", InvestigationAgent(db))
    graph.add_node("evidence", EvidenceAgent(db))
    graph.add_node("recommendation", RecommendationAgent())

    graph.set_entry_point("detection")
    graph.add_edge("detection", "policy")
    graph.add_conditional_edges(
        "policy",
        lambda state: "investigate" if state.get("should_investigate") else "skip",
        {"investigate": "investigation", "skip": END},
    )
    graph.add_edge("investigation", "evidence")
    graph.add_edge("evidence", "recommendation")
    graph.add_edge("recommendation", END)

    return graph.compile()
