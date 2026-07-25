import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.domain.models.transaction import Transaction, TransactionStatus
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreateRequest, TransactionFilterParams, TransactionListResponse, TransactionResponse


class TransactionService:
    """
    Business rules for transaction ingestion. Risk scoring itself is
    intentionally NOT done here with a fake/random number - real risk
    scoring is the Detection Agent's job (AI Agents phase). Manually
    created transactions start at risk_score=0 / status=NORMAL and get
    scored once that pipeline runs against them.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = TransactionRepository(db)

    def list_transactions(self, organization_id: uuid.UUID, filters: TransactionFilterParams) -> TransactionListResponse:
        items, total, total_pages = self.repo.list_paginated(organization_id, filters)
        return TransactionListResponse(
            items=[TransactionResponse(**item) for item in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )

    def get_transaction(self, organization_id: uuid.UUID, transaction_id: uuid.UUID) -> TransactionResponse:
        item = self.repo.get_by_id(organization_id, transaction_id)
        if item is None:
            raise ResourceNotFoundError("Transaction")
        return TransactionResponse(**item)

    def create_transaction(self, organization_id: uuid.UUID, payload: TransactionCreateRequest) -> TransactionResponse:
        transaction = Transaction(
            organization_id=organization_id,
            department_id=payload.department_id,
            vendor_id=payload.vendor_id,
            reference_code=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency.upper(),
            transaction_date=payload.transaction_date,
            status=TransactionStatus.NORMAL,
            risk_score=0,
            is_policy_violation=False,
        )
        created = self.repo.create(transaction)
        item = self.repo.get_by_id(organization_id, created.id)
        return TransactionResponse(**item)
