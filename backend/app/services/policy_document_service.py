import uuid

from sqlalchemy.orm import Session

from app.domain.models.document import Document
from app.domain.models.policy_chunk import PolicyChunk
from app.repositories.policy_chunk_repository import PolicyChunkRepository
from app.services import embedding_client

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def chunk_text(text: str) -> list[str]:
    """Simple fixed-size sliding-window chunking. Good enough for policy-length
    documents; a token-aware splitter would be a drop-in upgrade later."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return [c for c in chunks if c]


class PolicyDocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.chunks = PolicyChunkRepository(db)

    def process_document(self, document: Document) -> int:
        """Chunks and (if possible) embeds a policy document's extracted text. Returns chunk count."""
        self.chunks.delete_for_document(document.id)

        pieces = chunk_text(document.extracted_text or "")
        rows = []
        for i, piece in enumerate(pieces):
            embedding = embedding_client.embed_text(piece)  # None if no API key configured
            rows.append(
                PolicyChunk(
                    organization_id=document.organization_id,
                    document_id=document.id,
                    chunk_index=i,
                    chunk_text=piece,
                    embedding=embedding,
                )
            )
        if rows:
            self.chunks.bulk_create(rows)
        return len(rows)

    def search(self, organization_id: uuid.UUID, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = embedding_client.embed_text(query)

        if query_embedding is not None:
            rows = self.chunks.semantic_search(organization_id, query_embedding, top_k)
            if rows:
                return [
                    {"document_name": name, "chunk_text": chunk.chunk_text, "search_method": "semantic"}
                    for chunk, name in rows
                ]

        # No API key, or no embedded chunks matched - fall back to keyword search
        # rather than returning nothing or a fabricated similarity score.
        rows = self.chunks.keyword_search(organization_id, query, top_k)
        return [{"document_name": name, "chunk_text": chunk.chunk_text, "search_method": "keyword"} for chunk, name in rows]
