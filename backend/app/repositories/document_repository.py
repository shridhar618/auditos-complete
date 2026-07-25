import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.document import Document, DocumentCategory


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update(self, document: Document) -> Document:
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> Document | None:
        stmt = select(Document).where(Document.organization_id == organization_id, Document.id == document_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_org(self, organization_id: uuid.UUID, category: DocumentCategory | None = None) -> list[Document]:
        stmt = select(Document).where(Document.organization_id == organization_id)
        if category:
            stmt = stmt.where(Document.category == category)
        stmt = stmt.order_by(Document.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
