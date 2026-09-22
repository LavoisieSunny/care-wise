from fastapi import APIRouter
from app.schemas.calculator import (
    CostCalculationRequest,
    HospitalCostAnalysis,
    CompareHospitalsRequest,
    CompareHospitalsResponse
)
from app.services.calculator_service import calculator_service

router = APIRouter()

@router.post("/calculator/simulate", response_model=HospitalCostAnalysis, tags=["Calculator"])
async def simulate_out_of_pocket_cost(req: CostCalculationRequest):
    """Simulate out-of-pocket expenses and detect proportionate deduction risks for a single hospital and room."""
    return calculator_service.calculate_single(req)

@router.post("/calculator/compare", response_model=CompareHospitalsResponse, tags=["Calculator"])
async def compare_hospitals_side_by_side(req: CompareHospitalsRequest):
    """Compare multiple hospitals side-by-side with out-of-pocket breakdown and safe recommendations."""
    return calculator_service.compare_multiple(req)
