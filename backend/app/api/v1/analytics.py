from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse, dependencies=[Depends(require_permission("analytics:read"))])
def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).get_analytics(current_user.organization_id)
