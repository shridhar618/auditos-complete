import math
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.domain.models.investigation import InvestigationStatus
from app.domain.models.transaction import TransactionStatus
from app.domain.models.user import User
from app.repositories.agent_run_log_repository import AgentRunLogRepository
from app.repositories.investigation_repository import InvestigationRepository
from app.schemas.agent import AgentRunLogResponse
from app.schemas.investigation import (
    DismissInvestigationRequest,
    InvestigationDetailResponse,
    InvestigationListResponse,
    InvestigationResponse,
    ResolveInvestigationRequest,
)


class InvestigationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InvestigationRepository(db)
        self.logs = AgentRunLogRepository(db)

    def list_investigations(
        self, organization_id: uuid.UUID, status: InvestigationStatus | None, page: int, page_size: int
    ) -> InvestigationListResponse:
        items, total = self.repo.list_for_org(organization_id, status, page, page_size)
        return InvestigationListResponse(
            items=[self._to_response(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, math.ceil(total / page_size)),
        )

    def get_investigation(self, organization_id: uuid.UUID, investigation_id: uuid.UUID) -> InvestigationDetailResponse:
        investigation = self.repo.get_by_id(organization_id, investigation_id)
        if investigation is None:
            raise ResourceNotFoundError("Investigation")

        agent_logs = self.logs.list_for_investigation(investigation_id)
        base = self._to_response(investigation)
        return InvestigationDetailResponse(
            **base.model_dump(),
            evidence_json=investigation.evidence_json,
            resolution_notes=investigation.resolution_notes,
            agent_logs=[AgentRunLogResponse.model_validate(log) for log in agent_logs],
        )

    def resolve(
        self, organization_id: uuid.UUID, investigation_id: uuid.UUID, current_user: User, payload: ResolveInvestigationRequest
    ) -> InvestigationResponse:
        investigation = self.repo.get_by_id(organization_id, investigation_id)
        if investigation is None:
            raise ResourceNotFoundError("Investigation")

        investigation.status = InvestigationStatus.RESOLVED
        investigation.approved_by_user_id = current_user.id
        investigation.resolution_notes = payload.resolution_notes
        investigation.resolved_at = datetime.now(timezone.utc)
        self.repo.update(investigation)
        return self._to_response(investigation)

    def dismiss(
        self, organization_id: uuid.UUID, investigation_id: uuid.UUID, current_user: User, payload: DismissInvestigationRequest
    ) -> InvestigationResponse:
        investigation = self.repo.get_by_id(organization_id, investigation_id)
        if investigation is None:
            raise ResourceNotFoundError("Investigation")

        investigation.status = InvestigationStatus.DISMISSED
        investigation.approved_by_user_id = current_user.id
        investigation.resolution_notes = payload.resolution_notes
        investigation.resolved_at = datetime.now(timezone.utc)
        self.repo.update(investigation)

        # Dismissing means a human has determined this was a false positive -
        # clear the underlying transaction so it stops showing as at-risk.
        if investigation.transaction_id:
            transaction = self.repo.find_transaction(organization_id, investigation.transaction_id)
            if transaction:
                transaction.status = TransactionStatus.CLEARED
                self.repo.update_transaction(transaction)

        return self._to_response(investigation)

    @staticmethod
    def _to_response(investigation) -> InvestigationResponse:
        return InvestigationResponse(
            id=investigation.id,
            transaction_id=investigation.transaction_id,
            transaction_reference=investigation.transaction.reference_code if investigation.transaction else None,
            status=investigation.status,
            risk_level=investigation.risk_level,
            summary=investigation.summary,
            recommendation=investigation.recommendation,
            created_at=investigation.created_at,
            resolved_at=investigation.resolved_at,
        )
