import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.lookup import Department, Vendor


class LookupRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_departments(self, organization_id: uuid.UUID) -> list[Department]:
        stmt = select(Department).where(Department.organization_id == organization_id).order_by(Department.name)
        return list(self.db.execute(stmt).scalars().all())

    def list_vendors(self, organization_id: uuid.UUID) -> list[Vendor]:
        stmt = select(Vendor).where(Vendor.organization_id == organization_id).order_by(Vendor.name)
        return list(self.db.execute(stmt).scalars().all())
