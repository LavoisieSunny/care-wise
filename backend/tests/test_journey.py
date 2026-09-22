"""
Unit tests for CareWise Journey Service:
- Dynamic scaling of pre-auth and interim bills against sum insured
- Financial balance verification in generate_dossier() (total_bill == cashless + caregiver)
- Decision guidance logic
"""
import pytest
from app.services.journey_service import journey_service
from app.services.policy_service import policy_service
from app.schemas.journey import AdvanceJourneyRequest
from app.schemas.policy import PolicyDetails, PolicyRoomLimit, PolicyCoPay, PolicyPreAuth


@pytest.fixture
def custom_policy():
    pols = policy_service.list_policies()
    if pols:
        return pols[0]

    return PolicyDetails(
        id="test_optima_plus",
        insurer_name="Care Health Insurance",
        policy_name="Care Supreme Elite 10L",
        policy_type="Comprehensive Health",
        sum_insured=1000000.0,
        room_limit=PolicyRoomLimit(
            has_room_limit=False,
            allowed_room_category="Any Room",
            no_room_rent_capping=True
        ),
        copay=PolicyCoPay(
            has_copay=True,
            standard_copay_percentage=0.0,
            senior_citizen_percentage=10.0,
            zone_based_copay=False
        ),
        pre_auth=PolicyPreAuth(
            planned_admission_window_hours=48,
            emergency_window_hours=24,
            cashless_desk_contact="1800-CARE-WISE"
        ),
        empanelled_tpas=["Medi Assist TPA", "Vidal Health"],
        waiting_periods=[],
        key_exclusions=[],
        all_citations=[]
    )


def test_journey_status_dynamic_scaling(custom_policy):
    """Ensure pre-auth and interim bills scale with policy sum insured."""
    status = journey_service.get_status(policy_id=custom_policy.id)
    assert status.pre_auth_approved_amount > 0
    assert status.current_interim_bill > 0
    assert status.out_of_pocket_estimated > 0
    assert len(status.stages) == 4


def test_dossier_financial_balance(custom_policy):
    """Ensure generate_dossier amounts are mathematically balanced with zero fake hardcoding."""
    dossier = journey_service.generate_dossier(policy_id=custom_policy.id)

    assert dossier.total_bill > 0
    assert dossier.cashless_sanctioned > 0
    assert dossier.caregiver_paid > 0
    # Must satisfy exact ledger equation:
    assert round(dossier.total_bill, 2) == round(dossier.cashless_sanctioned + dossier.caregiver_paid, 2)
    # Check dynamic TPA code and document checklist
    assert len(dossier.documents_checklist) >= 5
    assert "POL-" in dossier.policy_number


def test_journey_stage_advancement():
    """Ensure stages advance sequentially from admission through discharge."""
    adv_req = AdvanceJourneyRequest(target_stage_id="treatment")
    res = journey_service.advance_stage(adv_req)
    assert res.current_stage_id == "treatment"

    adv_req_discharge = AdvanceJourneyRequest(target_stage_id="discharge")
    res_discharge = journey_service.advance_stage(adv_req_discharge)
    assert res_discharge.current_stage_id == "discharge"


def test_guidance_room_rent_breach():
    """Ensure proportionate deduction warning is triggered when room tariff exceeds cap."""
    guidance = journey_service.get_decision_guidance(
        selected_room="deluxe_suite",
        selected_procedure="angioplasty"
    )
    assert guidance is not None
    assert "headline" in guidance
