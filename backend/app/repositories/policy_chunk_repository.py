import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.models.document import Document
from app.domain.models.policy_chunk import PolicyChunk


class PolicyChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, chunks: list[PolicyChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()

    def delete_for_document(self, document_id: uuid.UUID) -> None:
        stmt = select(PolicyChunk).where(PolicyChunk.document_id == document_id)
        for chunk in self.db.execute(stmt).scalars().all():
            self.db.delete(chunk)
        self.db.commit()

    def semantic_search(self, organization_id: uuid.UUID, query_embedding: list[float], top_k: int = 5):
        """Cosine-distance nearest neighbor search over embedded chunks. Lower distance = more similar."""
        stmt = (
            select(PolicyChunk, Document.original_filename)
            .join(Document, PolicyChunk.document_id == Document.id)
            .where(PolicyChunk.organization_id == organization_id, PolicyChunk.embedding.is_not(None))
            .order_by(PolicyChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return self.db.execute(stmt).all()

    def keyword_search(self, organization_id: uuid.UUID, query: str, top_k: int = 5):
        """Fallback when no embedding is available (no API key, or chunk predates one being set)."""
        terms = [t for t in query.split() if len(t) > 2][:6] or [query]
        conditions = [PolicyChunk.chunk_text.ilike(f"%{term}%") for term in terms]

        stmt = (
            select(PolicyChunk, Document.original_filename)
            .join(Document, PolicyChunk.document_id == Document.id)
            .where(PolicyChunk.organization_id == organization_id, or_(*conditions))
            .limit(top_k)
        )
        return self.db.execute(stmt).all()
