from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.journey import (
    JourneyStatusResponse,
    AdvanceJourneyRequest,
    ClaimDossierResponse
)
from app.services.journey_service import journey_service

router = APIRouter()

@router.get("/journey/status", response_model=JourneyStatusResponse, tags=["Journey Tracker"])
async def get_journey_status(policy_id: Optional[str] = Query(None)):
    """Get active patient journey state, live interim metrics, and alerts dynamically derived from the policy."""
    return journey_service.get_status(policy_id=policy_id)

@router.get("/journey/guidance", tags=["Journey Tracker"])
async def get_decision_guidance(
    policy_id: Optional[str] = Query(None),
    room_type: str = Query("twin_sharing"),
    procedure: str = Query("angioplasty"),
    emergency_mode: bool = Query(False)
):
    """Dynamic AI justification and Next Best Action engine output for caregivers."""
    return journey_service.get_decision_guidance(
        policy_id=policy_id,
        selected_room=room_type,
        selected_procedure=procedure,
        emergency_mode=emergency_mode
    )

@router.post("/journey/advance", response_model=JourneyStatusResponse, tags=["Journey Tracker"])
async def advance_journey_stage(req: AdvanceJourneyRequest):
    """Advance or simulate transition between Admission, Treatment, Billing, and Discharge."""
    return journey_service.advance_stage(req)

@router.post("/journey/dossier", response_model=ClaimDossierResponse, tags=["Journey Tracker"])
async def generate_claim_dossier(policy_id: Optional[str] = Query(None)):
    """Generate final digital claim dossier and checklist for one-click discharge clearance."""
    return journey_service.generate_dossier(policy_id=policy_id)

