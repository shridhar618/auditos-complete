from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.domain.models.user import User
from app.repositories.lookup_repository import LookupRepository

router = APIRouter(prefix="/lookups", tags=["Lookups"])


class LookupOption(BaseModel):
    id: str
    name: str


@router.get("/departments", response_model=list[LookupOption])
def list_departments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    departments = LookupRepository(db).list_departments(current_user.organization_id)
    return [LookupOption(id=str(d.id), name=d.name) for d in departments]


@router.get("/vendors", response_model=list[LookupOption])
def list_vendors(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vendors = LookupRepository(db).list_vendors(current_user.organization_id)
    return [LookupOption(id=str(v.id), name=v.name) for v in vendors]
