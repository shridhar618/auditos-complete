import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.investigation import InvestigationStatus
from app.domain.models.user import User
from app.schemas.investigation import (
    DismissInvestigationRequest,
    InvestigationDetailResponse,
    InvestigationListResponse,
    InvestigationResponse,
    ResolveInvestigationRequest,
)
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=InvestigationListResponse, dependencies=[Depends(require_permission("investigations:read"))])
def list_investigations(
    status_filter: InvestigationStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InvestigationService(db).list_investigations(current_user.organization_id, status_filter, page, page_size)


@router.get(
    "/{investigation_id}",
    response_model=InvestigationDetailResponse,
    dependencies=[Depends(require_permission("investigations:read"))],
)
def get_investigation(
    investigation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InvestigationService(db).get_investigation(current_user.organization_id, investigation_id)


@router.post(
    "/{investigation_id}/resolve",
    response_model=InvestigationResponse,
    dependencies=[Depends(require_permission("investigations:approve"))],
)
def resolve_investigation(
    investigation_id: uuid.UUID,
    payload: ResolveInvestigationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InvestigationService(db).resolve(current_user.organization_id, investigation_id, current_user, payload)


@router.post(
    "/{investigation_id}/dismiss",
    response_model=InvestigationResponse,
    dependencies=[Depends(require_permission("investigations:approve"))],
)
def dismiss_investigation(
    investigation_id: uuid.UUID,
    payload: DismissInvestigationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InvestigationService(db).dismiss(current_user.organization_id, investigation_id, current_user, payload)
