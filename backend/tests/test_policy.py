"""
Unit tests for PolicyService:
- Sample policy ingestion
- Disk persistence in backend/app/data/uploaded/
- PyMuPDF text parsing & heuristic extraction
"""
import fitz
from pathlib import Path
from app.services.policy_service import policy_service
from app.core.database import SessionLocal, PolicyRecord
from app.schemas.policy import PolicyDetails, PolicyRoomLimit, PolicyCoPay, PolicyPreAuth


def test_list_and_get_sample_policies():
    """Ensure sample policies are loaded into database on boot."""
    policies = policy_service.list_policies()
    assert len(policies) >= 3

    p0 = policies[0]
    fetched = policy_service.get_policy(p0.id)
    assert fetched is not None
    assert fetched.id == p0.id
    assert fetched.sum_insured > 0


def test_policy_database_persistence():
    """Ensure user-uploaded policies persist to SQLite database."""
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

    # Persist via service
    policy_service._save_policy(policy)

    # Verify directly in DB
    db = SessionLocal()
    try:
        record = db.get(PolicyRecord, test_id)
        assert record is not None
        assert record.policy_name == "Star Comprehensive Demo Plan"
    finally:
        db.close()

    # Re-read via service
    reloaded = policy_service.get_policy(test_id)
    assert reloaded is not None
    assert reloaded.id == test_id
    assert reloaded.sum_insured == 750000.0

    # Clean up test artifact from DB
    db = SessionLocal()
    try:
        rec = db.get(PolicyRecord, test_id)
        if rec:
            db.delete(rec)
            db.commit()
    finally:
        db.close()


def test_parse_pdf_with_pymupdf():
    """Ensure PyMuPDF extracts text and creates PolicyUploadResponse and persists in DB."""
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

    # Verify saved in DB
    saved = policy_service.get_policy(res.policy.id)
    assert saved is not None
    assert saved.id == res.policy.id

    # Cleanup DB record
    db = SessionLocal()
    try:
        rec = db.get(PolicyRecord, res.policy.id)
        if rec:
            db.delete(rec)
            db.commit()
    finally:
        db.close()
