"""
Unit tests for PolicyService:
- Sample policy ingestion
- Disk persistence in backend/app/data/uploaded/
- PyMuPDF text parsing & heuristic extraction
"""
import fitz
from pathlib import Path
from app.services.policy_service import policy_service, UPLOADED_DATA_PATH
from app.schemas.policy import PolicyDetails, PolicyRoomLimit, PolicyCoPay, PolicyPreAuth


def test_list_and_get_sample_policies():
    """Ensure sample policies are loaded into memory on boot."""
    policies = policy_service.list_policies()
    assert len(policies) >= 3

    p0 = policies[0]
    fetched = policy_service.get_policy(p0.id)
    assert fetched is not None
    assert fetched.id == p0.id
    assert fetched.sum_insured > 0


def test_policy_disk_persistence(tmp_path):
    """Ensure user-uploaded policies persist to disk and reload on service restart."""
    test_id = "test_persisted_policy_999"
    policy = PolicyDetails(
        id=test_id,
        insurer_name="Star Health & Allied Insurance",
        policy_name="Star Comprehensive Demo Plan",
        policy_type="Individual Mediclaim",
        sum_insured=750000.0,
        room_limit=PolicyRoomLimit(
            has_room_limit=True,
            allowed_room_category="Single Standard",
            capped_amount_per_day=7500.0,
            no_room_rent_capping=False
        ),
        copay=PolicyCoPay(
            has_copay=False,
            standard_copay_percentage=0.0,
            senior_citizen_percentage=0.0
        ),
        pre_auth=PolicyPreAuth(
            planned_admission_window_hours=72,
            emergency_window_hours=24
        ),
        empanelled_tpas=["Medi Assist"],
        waiting_periods=[],
        key_exclusions=[],
        all_citations=[]
    )

    # Persist
    policy_service._persist_policy(policy)
    persisted_file = UPLOADED_DATA_PATH / f"{test_id}.json"
    assert persisted_file.exists()

    # Re-read from disk
    policy_service._load_sample_policies()
    reloaded = policy_service.get_policy(test_id)
    assert reloaded is not None
    assert reloaded.id == test_id
    assert reloaded.sum_insured == 750000.0

    # Clean up test artifact
    if persisted_file.exists():
        persisted_file.unlink()


def test_parse_pdf_with_pymupdf():
    """Ensure PyMuPDF extracts text and creates PolicyUploadResponse."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Policy Schedule: Star Health Insurance\n"
        "Sum Insured: Rs. 5,00,000\n"
        "Room Rent Limit: Capped at 1% of Sum Insured per day.\n"
        "Co-payment: Mandatory 10% co-payment for senior citizens aged 61+.\n"
        "Emergency Intimation: Pre-authorisation within 24 hours of admission."
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    res = policy_service.parse_pdf(pdf_bytes, filename="star_health_sample.pdf", mode="quick")
    assert res.success is True
    assert res.pages_processed == 1
    assert res.policy is not None
    assert res.policy.sum_insured > 0

    # Cleanup generated file
    persisted = UPLOADED_DATA_PATH / f"{res.policy.id}.json"
    if persisted.exists():
        persisted.unlink()
