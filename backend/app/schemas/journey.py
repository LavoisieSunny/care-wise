from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class JourneyAlert(BaseModel):
    id: str
    stage: str
    severity: str # "INFO", "WARNING", "CRITICAL", "SUCCESS"
    title: str
    message: str
    timestamp: str
    action_label: Optional[str] = None
    action_type: Optional[str] = None

class StageChecklistItem(BaseModel):
    id: str
    task: str
    completed: bool
    required: bool = True
    tip: str

class JourneyStageDetail(BaseModel):
    stage_id: str # "admission", "treatment", "billing", "discharge"
    title: str
    subtitle: str
    status: str # "COMPLETED", "IN_PROGRESS", "UPCOMING"
    metrics: Dict[str, Any]
    checklist: List[StageChecklistItem]
    alerts: List[JourneyAlert]

class JourneyStatusResponse(BaseModel):
    patient_name: str
    hospital_name: str
    policy_name: str
    admission_number: str
    current_stage_id: str
    pre_auth_approved_amount: float
    current_interim_bill: float
    out_of_pocket_estimated: float
    stages: List[JourneyStageDetail]
    active_alerts: List[JourneyAlert]

class AdvanceJourneyRequest(BaseModel):
    target_stage_id: str
    action: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class ClaimDossierResponse(BaseModel):
    dossier_id: str
    generated_at: str
    patient_name: str
    hospital_name: str
    policy_number: str
    total_bill: float
    cashless_sanctioned: float
    copay_settled: float
    caregiver_paid: float
    documents_checklist: List[str]
    tpa_submission_code: str
    summary_text: str
