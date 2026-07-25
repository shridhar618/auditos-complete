import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.document import DocumentCategory
from app.domain.models.user import User
from app.schemas.document import DocumentDetailResponse, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse], dependencies=[Depends(require_permission("documents:read"))])
def list_documents(
    category: DocumentCategory | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DocumentService(db).list_documents(current_user.organization_id, category)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("documents:write"))],
)
async def upload_document(
    file: UploadFile = File(...),
    category: DocumentCategory = Form(default=DocumentCategory.OTHER),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    return DocumentService(db).upload_document(
        organization_id=current_user.organization_id,
        uploaded_by_user_id=current_user.id,
        original_filename=file.filename or "untitled",
        content_type=file.content_type,
        file_bytes=file_bytes,
        category=category,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    dependencies=[Depends(require_permission("documents:read"))],
)
def get_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DocumentService(db).get_document(current_user.organization_id, document_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("documents:write"))],
)
def delete_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    DocumentService(db).delete_document(current_user.organization_id, document_id)
