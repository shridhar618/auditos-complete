from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.domain.models.document import DocumentCategory
from app.domain.models.user import User
from app.schemas.document import DocumentResponse, PolicySearchRequest, PolicySearchResponse
from app.services import embedding_client
from app.services.document_service import DocumentService
from app.services.policy_document_service import PolicyDocumentService

router = APIRouter(prefix="/policies", tags=["Policy Center"])


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("policies:write"))],
)
async def upload_policy_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Uploads a policy/regulation document (PDF, DOCX, or text) and chunks+embeds it for search."""
    file_bytes = await file.read()
    return DocumentService(db).upload_document(
        organization_id=current_user.organization_id,
        uploaded_by_user_id=current_user.id,
        original_filename=file.filename or "untitled",
        content_type=file.content_type,
        file_bytes=file_bytes,
        category=DocumentCategory.POLICY,
    )


@router.post(
    "/search",
    response_model=PolicySearchResponse,
    dependencies=[Depends(require_permission("policies:read"))],
)
def search_policies(
    payload: PolicySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = PolicyDocumentService(db).search(current_user.organization_id, payload.query)
    method_used = results[0]["search_method"] if results else ("semantic" if embedding_client.is_available() else "keyword")
    return PolicySearchResponse(results=results, search_method_used=method_used)
