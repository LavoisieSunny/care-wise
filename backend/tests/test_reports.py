"""
Unit tests for Claim Readiness Report service, PDF rendering, and API endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.services.policy_service import policy_service
from app.services.calculator_service import calculator_service
from app.services.report_service import report_service
from app.services.report_pdf import render_claim_readiness_pdf
from app.schemas.calculator import CompareHospitalsRequest
from app.schemas.report import ClaimReadinessReportRequest

client = TestClient(app)


def test_claim_readiness_report_service_and_pdf():
    policies = policy_service.list_policies()
    assert len(policies) > 0
    policy = policies[0]

    # Run cost comparison
    comp_req = CompareHospitalsRequest(
        policy_id=policy.id,
        hospital_ids=["hosp_sanjeevani", "hosp_city_heart", "hosp_carewell"],
        procedure_code="angioplasty",
        room_type="twin_sharing",
        stay_days=3,
        patient_age=55
    )
    comparison = calculator_service.compare_multiple(comp_req)
    assert len(comparison.comparisons) == 3

    # Generate report via service
    report_req = ClaimReadinessReportRequest(
        policy_id=policy.id,
        comparison=comparison
    )
    report = report_service.generate_report(report_req)
    assert report.report_id.startswith("CW-RPT-")
    assert report.policy_name == policy.policy_name
    assert len(report.ai_summary) > 20
    assert len(report.comparisons) == 3

    # Render PDF
    pdf_bytes = render_claim_readiness_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_api_claim_readiness_endpoints():
    policies = policy_service.list_policies()
    policy = policies[0]

    comp_req = CompareHospitalsRequest(
        policy_id=policy.id,
        hospital_ids=["hosp_sanjeevani", "hosp_city_heart"],
        procedure_code="appendectomy",
        room_type="twin_sharing",
        stay_days=2,
        patient_age=45
    )
    comparison = calculator_service.compare_multiple(comp_req)

    payload = {
        "policy_id": policy.id,
        "comparison": comparison.model_dump()
    }
    import uuid
    uid = uuid.uuid4().hex[:8]
    reg_res = client.post("/api/v1/auth/register", json={
        "email": f"report_tester_{uid}@carewise.org",
        "password": "Password123!",
        "name": f"Report Tester {uid}"
    })
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test JSON endpoint
    res_json = client.post("/api/v1/reports/claim-readiness", json=payload, headers=headers)
    assert res_json.status_code == 200
    data = res_json.json()
    assert "report_id" in data
    assert "ai_summary" in data

    # Test PDF download endpoint
    res_pdf = client.post("/api/v1/reports/claim-readiness/pdf", json=payload, headers=headers)
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert "CareWise_Claim_Readiness_Report.pdf" in res_pdf.headers.get("content-disposition", "")
    assert len(res_pdf.content) > 1000
