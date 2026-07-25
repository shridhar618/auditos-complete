import uuid
from datetime import datetime

from pydantic import BaseModel

from app.domain.models.document import DocumentCategory, DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    content_type: str | None
    file_size_bytes: int
    category: DocumentCategory
    status: DocumentStatus
    extraction_method: str | None
    processing_error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    extracted_text: str | None


class PolicySearchRequest(BaseModel):
    query: str


class PolicySearchResult(BaseModel):
    document_name: str
    chunk_text: str
    search_method: str  # "semantic" | "keyword"


class PolicySearchResponse(BaseModel):
    results: list[PolicySearchResult]
    search_method_used: str
