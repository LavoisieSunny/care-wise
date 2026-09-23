import uuid
from datetime import datetime
from app.services.policy_service import policy_service
from app.services.llm_client import LLMClient
from app.schemas.report import ClaimReadinessReportRequest, ClaimReadinessReportResponse

PLAIN_SUMMARY_SYSTEM_PROMPT = """You are CareWise AI. Explain a health insurance policy to a worried
family member in plain, warm, simple English — no jargon.
In 4-5 sentences max, cover: what's covered, the single biggest financial risk to watch for
(like room rent capping or co-pay), and one clear action they should take.
Return ONLY plain text, no markdown, no JSON."""


class ReportService:
    def __init__(self):
        self.llm = LLMClient()

    def generate_ai_summary(self, policy) -> str:
        user_prompt = f"""Policy: {policy.policy_name} by {policy.insurer_name}
Sum Insured: Rs.{policy.sum_insured:,.0f}
Room Limit: {policy.room_limit.allowed_room_category}, capped at Rs.{policy.room_limit.capped_amount_per_day or 0:,.0f}/day, proportionate deduction applies: {policy.room_limit.proportionate_deduction_applies}
Co-pay: {policy.copay.standard_percentage}% standard, {policy.copay.senior_citizen_percentage}% senior citizen
Key Exclusions: {', '.join(policy.key_exclusions[:5])}
"""
        result = self.llm._execute_llm(PLAIN_SUMMARY_SYSTEM_PROMPT, user_prompt)
        if not result:
            return (
                f"Your {policy.policy_name} policy covers up to Rs.{policy.sum_insured:,.0f}. "
                f"Watch out for the room rent limit — choosing a higher room category than allowed can trigger "
                f"a proportionate deduction, reducing your payout. Confirm your room choice with the hospital's "
                f"insurance desk before admission."
            )
        return result.strip()

    def generate_report(self, req: ClaimReadinessReportRequest) -> ClaimReadinessReportResponse:
        policy = policy_service.get_policy(req.policy_id)
        if not policy:
            raise ValueError("Policy not found")

        ai_summary = self.generate_ai_summary(policy)

        # Resolve friendly hospital name if hospital ID matches a comparison
        recommended_name = req.comparison.recommended_hospital_id
        for comp in req.comparison.comparisons:
            if comp.hospital_id == req.comparison.recommended_hospital_id:
                recommended_name = comp.hospital_name
                break

        return ClaimReadinessReportResponse(
            report_id=f"CW-RPT-{uuid.uuid4().hex[:8].upper()}",
            generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p"),
            policy_name=policy.policy_name,
            ai_summary=ai_summary,
            recommended_hospital=recommended_name,
            savings_vs_riskiest=req.comparison.savings_vs_riskiest,
            comparisons=req.comparison.comparisons,
        )


report_service = ReportService()
