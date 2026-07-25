import os
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, ResourceNotFoundError
from app.domain.models.document import Document, DocumentCategory, DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.repositories.policy_chunk_repository import PolicyChunkRepository
from app.services import text_extraction_service
from app.services.policy_document_service import PolicyDocumentService


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)

    def upload_document(
        self,
        organization_id: uuid.UUID,
        uploaded_by_user_id: uuid.UUID,
        original_filename: str,
        content_type: str | None,
        file_bytes: bytes,
        category: DocumentCategory,
    ) -> Document:
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise FileTooLargeError(settings.MAX_UPLOAD_SIZE_MB)

        storage_path = self._save_to_disk(organization_id, original_filename, file_bytes)

        document = Document(
            organization_id=organization_id,
            uploaded_by_user_id=uploaded_by_user_id,
            original_filename=original_filename,
            storage_path=storage_path,
            content_type=content_type,
            file_size_bytes=len(file_bytes),
            category=category,
            status=DocumentStatus.PROCESSING,
        )
        document = self.repo.create(document)

        result = text_extraction_service.extract_text(storage_path, content_type)
        document.extracted_text = result.text
        document.extraction_method = result.method
        document.processing_error = result.error
        document.status = DocumentStatus.READY if result.text.strip() else DocumentStatus.FAILED
        document = self.repo.update(document)

        if category == DocumentCategory.POLICY and document.status == DocumentStatus.READY:
            PolicyDocumentService(self.db).process_document(document)

        return document

    def list_documents(self, organization_id: uuid.UUID, category: DocumentCategory | None) -> list[Document]:
        return self.repo.list_for_org(organization_id, category)

    def get_document(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        document = self.repo.get_by_id(organization_id, document_id)
        if document is None:
            raise ResourceNotFoundError("Document")
        return document

    def delete_document(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> None:
        document = self.get_document(organization_id, document_id)
        PolicyChunkRepository(self.db).delete_for_document(document.id)
        try:
            if os.path.exists(document.storage_path):
                os.remove(document.storage_path)
        except OSError:
            pass  # best-effort - don't fail the delete over a filesystem hiccup
        self.repo.delete(document)

    @staticmethod
    def _save_to_disk(organization_id: uuid.UUID, original_filename: str, file_bytes: bytes) -> str:
        org_dir = os.path.join(settings.UPLOAD_DIR, str(organization_id))
        os.makedirs(org_dir, exist_ok=True)

        safe_name = f"{uuid.uuid4().hex}_{os.path.basename(original_filename)}"
        full_path = os.path.join(org_dir, safe_name)
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return full_path
