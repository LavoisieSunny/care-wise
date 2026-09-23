from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.api.v1 import (
    health, auth, policies, hospitals, calculator, rag, journey, sos, reports
)

api_router = APIRouter()

# Public — no auth required
api_router.include_router(health.router)
api_router.include_router(auth.router)

# Protected — every request needs a valid Bearer token
protected = APIRouter(dependencies=[Depends(get_current_user)])
protected.include_router(policies.router)
protected.include_router(hospitals.router)
protected.include_router(calculator.router)
protected.include_router(rag.router)
protected.include_router(journey.router)
protected.include_router(sos.router)
protected.include_router(reports.router)
api_router.include_router(protected)
