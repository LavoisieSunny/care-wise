from typing import List
from pydantic import BaseModel
from .calculator import HospitalCostAnalysis, CompareHospitalsResponse


class ClaimReadinessReportRequest(BaseModel):
    policy_id: str
    comparison: CompareHospitalsResponse


class ClaimReadinessReportResponse(BaseModel):
    report_id: str
    generated_at: str
    policy_name: str
    ai_summary: str
    recommended_hospital: str
    savings_vs_riskiest: float
    comparisons: List[HospitalCostAnalysis]
