import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.user import User
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionFilterParams,
    TransactionListResponse,
    TransactionResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "",
    response_model=TransactionListResponse,
    dependencies=[Depends(require_permission("transactions:read"))],
)
def list_transactions(
    filters: TransactionFilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TransactionService(db).list_transactions(current_user.organization_id, filters)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    dependencies=[Depends(require_permission("transactions:read"))],
)
def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TransactionService(db).get_transaction(current_user.organization_id, transaction_id)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("transactions:write"))],
)
def create_transaction(
    payload: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TransactionService(db).create_transaction(current_user.organization_id, payload)
