from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ClauseCitation(BaseModel):
    clause_id: str
    section: str
    page_number: int
    clause_title: str
    exact_text: str
    tag: str = "TERMS"
    confidence: float = 1.0

class PolicyRoomLimit(BaseModel):
    capped_amount_per_day: Optional[float] = None
    percentage_of_sum_insured: Optional[float] = None
    no_room_rent_capping: bool = False
    allowed_room_category: str = "Standard Single AC"
    proportionate_deduction_applies: bool = True
    citation: Optional[ClauseCitation] = None

class PolicyCoPay(BaseModel):
    standard_percentage: float = 0.0
    senior_citizen_percentage: float = 0.0
    zone_based_copay: float = 0.0
    citation: Optional[ClauseCitation] = None

class PolicyPreAuth(BaseModel):
    emergency_window_hours: int = 24
    planned_window_hours: int = 48
    citation: Optional[ClauseCitation] = None

class PolicyDetails(BaseModel):
    id: str
    insurer_name: str
    policy_name: str
    policy_type: str = "Comprehensive Health Insurance"
    sum_insured: float
    room_limit: PolicyRoomLimit
    icu_limit_per_day: Optional[float] = None
    copay: PolicyCoPay
    pre_auth: PolicyPreAuth
    has_consumables_rider: bool = False
    empanelled_tpas: List[str]
    waiting_periods: List[Dict[str, Any]]
    key_exclusions: List[str]
    all_citations: List[ClauseCitation]
    raw_text_pages: Optional[Dict[str, str]] = None

class PolicyListResponse(BaseModel):
    policies: List[PolicyDetails]

class PolicyUploadResponse(BaseModel):
    success: bool
    message: str
    policy: PolicyDetails
    pages_processed: int
    confidence_score: float
    upload_id: Optional[str] = None
    extraction_mode: Optional[str] = "quick"
