import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.models.investigation import Investigation, InvestigationStatus
from app.domain.models.transaction import Transaction


class InvestigationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, investigation: Investigation) -> Investigation:
        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)
        return investigation

    def get_by_id(self, organization_id: uuid.UUID, investigation_id: uuid.UUID) -> Investigation | None:
        stmt = (
            select(Investigation)
            .options(joinedload(Investigation.transaction))
            .where(Investigation.organization_id == organization_id, Investigation.id == investigation_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_for_org(
        self, organization_id: uuid.UUID, status: InvestigationStatus | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Investigation], int]:
        stmt = (
            select(Investigation)
            .options(joinedload(Investigation.transaction))
            .where(Investigation.organization_id == organization_id)
        )
        if status:
            stmt = stmt.where(Investigation.status == status)
        stmt = stmt.order_by(Investigation.created_at.desc())

        count_stmt = select(Investigation.id).where(Investigation.organization_id == organization_id)
        if status:
            count_stmt = count_stmt.where(Investigation.status == status)
        total = len(self.db.execute(count_stmt).all())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.execute(stmt).unique().scalars().all())
        return items, total

    def update(self, investigation: Investigation) -> Investigation:
        self.db.commit()
        self.db.refresh(investigation)
        return investigation

    def find_transaction(self, organization_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.organization_id == organization_id, Transaction.id == transaction_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_transaction(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
