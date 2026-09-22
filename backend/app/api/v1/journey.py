from fastapi import APIRouter
from app.schemas.journey import (
    JourneyStatusResponse,
    AdvanceJourneyRequest,
    ClaimDossierResponse
)
from app.services.journey_service import journey_service

router = APIRouter()

@router.get("/journey/status", response_model=JourneyStatusResponse, tags=["Journey Tracker"])
async def get_journey_status():
    """Get active patient journey state, live interim metrics, and alerts across stages."""
    return journey_service.get_status()

@router.post("/journey/advance", response_model=JourneyStatusResponse, tags=["Journey Tracker"])
async def advance_journey_stage(req: AdvanceJourneyRequest):
    """Advance or simulate transition between Admission, Treatment, Billing, and Discharge."""
    return journey_service.advance_stage(req)

@router.post("/journey/dossier", response_model=ClaimDossierResponse, tags=["Journey Tracker"])
async def generate_claim_dossier():
    """Generate final digital claim dossier and checklist for one-click discharge clearance."""
    return journey_service.generate_dossier()
