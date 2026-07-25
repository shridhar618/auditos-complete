from pydantic import BaseModel


class RiskMatrixCell(BaseModel):
    department: str
    risk_band: str
    count: int


class InvestigationTimelinePoint(BaseModel):
    week: str
    total: int
    resolved: int
    dismissed: int
    pending: int


class ReviewerActivity(BaseModel):
    reviewer_name: str
    total_decided: int
    resolved: int
    dismissed: int


class AnalyticsResponse(BaseModel):
    risk_matrix: list[RiskMatrixCell]
    investigation_timeline: list[InvestigationTimelinePoint]
    reviewer_activity: list[ReviewerActivity]
