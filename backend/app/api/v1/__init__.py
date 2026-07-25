from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.documents import router as documents_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.lookups import router as lookups_router
from app.api.v1.policies import router as policies_router
from app.api.v1.reports import router as reports_router
from app.api.v1.roles import router as roles_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(dashboard_router)
api_router.include_router(transactions_router)
api_router.include_router(lookups_router)
api_router.include_router(investigations_router)
api_router.include_router(agents_router)
api_router.include_router(documents_router)
api_router.include_router(policies_router)
api_router.include_router(analytics_router)
api_router.include_router(reports_router)
