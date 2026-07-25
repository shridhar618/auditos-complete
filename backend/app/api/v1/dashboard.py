from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    dependencies=[Depends(require_permission("dashboard:read"))],
)
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_summary(current_user.organization_id)
