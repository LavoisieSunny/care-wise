from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SOSShareRequest(BaseModel):
    patient_name: str = "Ramesh Sharma"
    hospital_name: str = "Sanjeevani Multispeciality Hospital"
    emergency_contact: str = "+91 80 4122 8899"
    policy_name: str = "Star Health Family Health Optima"
    room_cap: str = "₹5,000/day (Twin Sharing)"
    tpa_name: str = "Medi Assist TPA"
    pre_auth_status: str = "Initial Sanction: ₹75,000"

class SOSShareResponse(BaseModel):
    whatsapp_text: str
    shareable_url: str
    action_checklist: list[str]

@router.post("/sos/generate", response_model=SOSShareResponse, tags=["Emergency SOS"])
async def generate_sos_share(req: SOSShareRequest):
    """Generate family emergency broadcast message and rapid hospital arrival checklist."""
    msg = (
        f"🚨 *CAREWAISE EMERGENCY FAMILY ALERT*\n\n"
        f"👤 *Patient*: {req.patient_name}\n"
        f"🏥 *Hospital*: {req.hospital_name}\n"
        f"📞 *Emergency Desk*: {req.emergency_contact}\n"
        f"🛡️ *Insurance*: {req.policy_name}\n"
        f"🏢 *TPA*: {req.tpa_name}\n"
        f"✅ *Status*: {req.pre_auth_status}\n\n"
        f"⚠️ *CRITICAL INSTRUCTION FOR FAMILY AT DESK*:\n"
        f"• Request *{req.room_cap}* ONLY.\n"
        f"• Do NOT accept room upgrades to Deluxe/Suite to avoid severe proportionate deduction penalties!\n"
        f"• Hand over patient Aadhaar card at TPA counter.\n\n"
        f"Live tracking link: https://carewise.health/track/ADM-2026-89410"
    )

    checklist = [
        "Reach hospital Emergency TPA Desk",
        f"Provide Policy Details: {req.policy_name}",
        f"Confirm Room Type is strictly within {req.room_cap}",
        "Keep treating doctor's admission advice signed"
    ]

    return SOSShareResponse(
        whatsapp_text=msg,
        shareable_url="https://carewise.health/track/ADM-2026-89410",
        action_checklist=checklist
    )
