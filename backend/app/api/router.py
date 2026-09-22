from fastapi import APIRouter
from app.api.v1 import (
    health,
    policies,
    hospitals,
    calculator,
    rag,
    journey,
    sos
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(policies.router)
api_router.include_router(hospitals.router)
api_router.include_router(calculator.router)
api_router.include_router(rag.router)
api_router.include_router(journey.router)
api_router.include_router(sos.router)
