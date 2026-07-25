import uuid

from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsResponse


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def get_analytics(self, organization_id: uuid.UUID) -> AnalyticsResponse:
        return AnalyticsResponse(
            risk_matrix=self.repo.risk_matrix(organization_id),
            investigation_timeline=self.repo.investigation_timeline(organization_id),
            reviewer_activity=self.repo.reviewer_activity(organization_id),
        )
