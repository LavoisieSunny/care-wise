from fastapi import APIRouter, Response
from app.schemas.report import ClaimReadinessReportRequest, ClaimReadinessReportResponse
from app.services.report_service import report_service
from app.services.report_pdf import render_claim_readiness_pdf
from app.core.audit_log import record_event

router = APIRouter()


@router.post("/reports/claim-readiness", response_model=ClaimReadinessReportResponse, tags=["Reports"])
async def generate_claim_readiness_report(req: ClaimReadinessReportRequest):
    result = report_service.generate_report(req)
    record_event(action="report.generate_claim_readiness", target_type="policy", target_id=req.policy_id)
    return result


@router.post("/reports/claim-readiness/pdf", tags=["Reports"])
async def download_claim_readiness_pdf(req: ClaimReadinessReportRequest):
    report = report_service.generate_report(req)
    pdf_bytes = render_claim_readiness_pdf(report)
    record_event(action="report.download_claim_readiness_pdf", target_type="policy", target_id=req.policy_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=CareWise_Claim_Readiness_Report.pdf"}
    )
