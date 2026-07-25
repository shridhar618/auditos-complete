import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.domain.models.transaction import TransactionStatus


class TransactionCreateRequest(BaseModel):
    department_id: uuid.UUID | None = None
    vendor_id: uuid.UUID | None = None
    description: str | None = None
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    transaction_date: date


class TransactionFilterParams(BaseModel):
    status: TransactionStatus | None = None
    department_id: uuid.UUID | None = None
    vendor_id: uuid.UUID | None = None
    search: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TransactionResponse(BaseModel):
    id: uuid.UUID
    reference_code: str
    description: str | None
    amount: float
    currency: str
    transaction_date: date
    status: TransactionStatus
    risk_score: int
    is_policy_violation: bool
    department_name: str | None
    vendor_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
