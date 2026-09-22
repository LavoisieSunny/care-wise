from typing import List, Dict, Optional
from pydantic import BaseModel

class BedAvailability(BaseModel):
    icu: int
    general: int
    single_private: int
    deluxe: int
    status: str = "AVAILABLE"

class RoomTariffs(BaseModel):
    general: float
    twin_sharing: float
    single_private: float
    deluxe_suite: float

class Hospital(BaseModel):
    id: str
    name: str
    tagline: str
    city: str
    locality: str
    distance_km: float
    rating: float
    reviews_count: int
    emergency_contact: str
    emergency_24x7: bool = True
    specialties: List[str]
    empanelled_tpas: List[str]
    network_status: str # "CASHLESS_NETWORK", "REIMBURSEMENT_ONLY", "NON_NETWORK"
    bed_availability: BedAvailability
    room_tariffs: RoomTariffs
    estimated_ambulance_eta_mins: int = 15

class HospitalFilterRequest(BaseModel):
    policy_id: Optional[str] = None
    locality: Optional[str] = None
    max_distance_km: Optional[float] = 20.0
    specialty: Optional[str] = None
    only_cashless: bool = False
    emergency_mode: bool = False

class HospitalListResponse(BaseModel):
    hospitals: List[Hospital]
    total: int
    active_policy_id: Optional[str] = None
    nearest_cashless_id: Optional[str] = None
