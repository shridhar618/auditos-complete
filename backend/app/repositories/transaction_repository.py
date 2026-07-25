import math
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.models.lookup import Department, Vendor
from app.domain.models.transaction import Transaction
from app.schemas.transaction import TransactionFilterParams


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, organization_id: uuid.UUID):
        return (
            select(
                Transaction,
                Department.name.label("department_name"),
                Vendor.name.label("vendor_name"),
            )
            .outerjoin(Department, Transaction.department_id == Department.id)
            .outerjoin(Vendor, Transaction.vendor_id == Vendor.id)
            .where(Transaction.organization_id == organization_id)
        )

    def list_paginated(self, organization_id: uuid.UUID, filters: TransactionFilterParams):
        stmt = self._base_query(organization_id)

        if filters.status:
            stmt = stmt.where(Transaction.status == filters.status)
        if filters.department_id:
            stmt = stmt.where(Transaction.department_id == filters.department_id)
        if filters.vendor_id:
            stmt = stmt.where(Transaction.vendor_id == filters.vendor_id)
        if filters.date_from:
            stmt = stmt.where(Transaction.transaction_date >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(Transaction.transaction_date <= filters.date_to)
        if filters.search:
            like = f"%{filters.search}%"
            stmt = stmt.where(or_(Transaction.reference_code.ilike(like), Transaction.description.ilike(like)))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        stmt = (
            stmt.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        rows = self.db.execute(stmt).all()

        items = []
        for txn, department_name, vendor_name in rows:
            items.append(
                {
                    "id": txn.id,
                    "reference_code": txn.reference_code,
                    "description": txn.description,
                    "amount": float(txn.amount),
                    "currency": txn.currency,
                    "transaction_date": txn.transaction_date,
                    "status": txn.status,
                    "risk_score": txn.risk_score,
                    "is_policy_violation": txn.is_policy_violation,
                    "department_name": department_name,
                    "vendor_name": vendor_name,
                    "created_at": txn.created_at,
                }
            )

        total_pages = max(1, math.ceil(total / filters.page_size))
        return items, total, total_pages

    def get_by_id(self, organization_id: uuid.UUID, transaction_id: uuid.UUID):
        stmt = self._base_query(organization_id).where(Transaction.id == transaction_id)
        row = self.db.execute(stmt).first()
        if row is None:
            return None
        txn, department_name, vendor_name = row
        return {
            "id": txn.id,
            "reference_code": txn.reference_code,
            "description": txn.description,
            "amount": float(txn.amount),
            "currency": txn.currency,
            "transaction_date": txn.transaction_date,
            "status": txn.status,
            "risk_score": txn.risk_score,
            "is_policy_violation": txn.is_policy_violation,
            "department_name": department_name,
            "vendor_name": vendor_name,
            "created_at": txn.created_at,
        }

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
