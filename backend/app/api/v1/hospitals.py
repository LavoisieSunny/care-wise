from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.hospital import Hospital, HospitalListResponse, HospitalFilterRequest
from app.services.hospital_service import hospital_service

router = APIRouter()

@router.get("/hospitals", response_model=HospitalListResponse, tags=["Hospitals"])
async def search_hospitals(
    policy_id: Optional[str] = Query(None, description="Active policy ID to match cashless empanelment"),
    locality: Optional[str] = Query(None, description="Locality or city filter"),
    max_distance_km: Optional[float] = Query(25.0, description="Max radius in km"),
    specialty: Optional[str] = Query(None, description="Medical specialty filter"),
    only_cashless: bool = Query(False, description="Show only 100% cashless network hospitals"),
    emergency_mode: bool = Query(False, description="Enable 2 AM Emergency Mode (filters for 24x7 ICU)")
):
    """Search and filter hospitals based on location, cashless network compatibility, and bed availability."""
    req = HospitalFilterRequest(
        policy_id=policy_id,
        locality=locality,
        max_distance_km=max_distance_km,
        specialty=specialty,
        only_cashless=only_cashless,
        emergency_mode=emergency_mode
    )
    return hospital_service.filter_hospitals(req)

@router.get("/hospitals/{hospital_id}", response_model=Hospital, tags=["Hospitals"])
async def get_hospital_details(hospital_id: str):
    """Retrieve details, bed status, and tariffs for a single hospital."""
    hospital = hospital_service.get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital
