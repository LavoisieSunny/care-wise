from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class CostCalculationRequest(BaseModel):
    policy_id: str
    hospital_id: str
    procedure_code: str
    room_type: str = "twin_sharing" # general, twin_sharing, single_private, deluxe_suite
    stay_days: Optional[int] = None
    patient_age: int = 52

class CostBreakdownItem(BaseModel):
    category: str
    hospital_charged: float
    insurer_covered: float
    caregiver_out_of_pocket: float
    notes: str

class HospitalCostAnalysis(BaseModel):
    hospital_id: str
    hospital_name: str
    network_status: str # CASHLESS_NETWORK, REIMBURSEMENT_ONLY, NON_NETWORK
    procedure_name: str
    room_type: str
    room_type_label: str
    stay_days: int
    daily_room_charge: float
    policy_room_limit_daily: float
    proportionate_deduction_triggered: bool
    proportionate_deduction_penalty: float
    copay_percentage: float
    copay_amount: float
    non_medical_consumables: float
    total_bill: float
    insurer_settlement: float
    estimated_out_of_pocket: float
    risk_tier: str # RECOMMENDED, FINANCIAL_RISK, NOT_ELIGIBLE
    risk_reasons: List[str]
    breakdown: List[CostBreakdownItem]

class CompareHospitalsRequest(BaseModel):
    policy_id: str
    hospital_ids: List[str]
    procedure_code: str
    room_type: str = "twin_sharing"
    stay_days: Optional[int] = None
    patient_age: int = 52

class CompareHospitalsResponse(BaseModel):
    policy_id: str
    policy_name: str
    procedure_name: str
    comparisons: List[HospitalCostAnalysis]
    recommended_hospital_id: str
    savings_vs_riskiest: float
