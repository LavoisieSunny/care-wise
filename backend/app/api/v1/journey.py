from typing import Optional
from fastapi import APIRouter, Query, Response, Body
from app.schemas.journey import (
    JourneyStatusResponse,
    AdvanceJourneyRequest,
    ClaimDossierResponse
)
from app.services.journey_service import journey_service
from app.core.audit_log import record_event

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
    result = journey_service.advance_stage(req)
    record_event(
        action="journey.advance_stage",
        target_type="journey",
        target_id=getattr(req, "policy_id", None),
        detail={"target_stage": getattr(req, "target_stage_id", None)},
    )
    return result

@router.post("/journey/dossier", response_model=ClaimDossierResponse, tags=["Journey Tracker"])
async def generate_claim_dossier(policy_id: Optional[str] = Query(None)):
    """Generate final digital claim dossier and checklist for one-click discharge clearance."""
    result = journey_service.generate_dossier(policy_id=policy_id)
    record_event(action="journey.generate_dossier", target_type="journey", target_id=policy_id)
    return result

@router.get("/journey/dossier/pdf", tags=["Journey Tracker"])
async def download_claim_dossier_pdf(policy_id: Optional[str] = Query(None)):
    """Generate and download official CareWise Digital Claim & Care Dossier PDF."""
    pdf_bytes = journey_service.generate_dossier_pdf(policy_id=policy_id)
    record_event(action="journey.download_dossier_pdf", target_type="journey", target_id=policy_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=CareWise_Claim_Dossier.pdf"
        }
    )

@router.post("/journey/notify-caregiver", tags=["Journey Tracker"])
async def notify_caregiver(
    policy_id: Optional[str] = Query(None),
    phone_number: str = Body("+91 98765 43210", embed=True)
):
    """Trigger real-time WhatsApp alert to caregiver for journey updates and claim dossier."""
    result = journey_service.trigger_caregiver_notification(policy_id=policy_id, phone_number=phone_number)
    record_event(
        action="journey.notify_caregiver_whatsapp",
        target_type="caregiver",
        detail={"phone": phone_number, "status": result.get("status")},
    )
    return result
