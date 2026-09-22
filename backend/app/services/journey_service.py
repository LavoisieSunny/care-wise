import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.journey import (
    JourneyStatusResponse,
    JourneyStageDetail,
    JourneyAlert,
    StageChecklistItem,
    AdvanceJourneyRequest,
    ClaimDossierResponse
)
from app.schemas.policy import PolicyDetails
from app.services.policy_service import policy_service
from app.services.dossier_pdf import render_dossier_pdf


class JourneyService:
    def __init__(self):
        self._current_stage_id = "admission"
        self._patient_name = "Ramesh Sharma (Age 58)"
        self._hospital_name = "Sanjeevani Multispeciality Hospital"
        self._admission_number = "ADM-2026-89410"

    def _resolve_policy(self, policy_id: Optional[str]) -> PolicyDetails:
        if policy_id:
            pol = policy_service.get_policy(policy_id)
            if pol:
                return pol
        pols = policy_service.list_policies()
        return pols[0] if pols else None

    def get_status(self, policy_id: Optional[str] = None) -> JourneyStatusResponse:
        policy = self._resolve_policy(policy_id)
        if not policy:
            raise ValueError("No policies available to derive journey.")

        sum_insured = policy.sum_insured
        room_cap = policy.room_limit.capped_amount_per_day or (sum_insured * 0.01)
        no_room_cap = policy.room_limit.no_room_rent_capping
        category = policy.room_limit.allowed_room_category
        copay_senior = policy.copay.senior_citizen_percentage
        notice_hours = policy.pre_auth.emergency_window_hours
        tpa_name = policy.empanelled_tpas[0] if policy.empanelled_tpas else "Medi Assist TPA"

        # Dynamically scale pre-auth sanction to policy sum insured
        pre_auth_approved = min(175000.0, max(50000.0, sum_insured * 0.15))
        
        # Scale interim bills according to current stage
        if self._current_stage_id == "admission":
            interim_bill = round(pre_auth_approved * 0.82, 0)
            oop_est = round(interim_bill * (copay_senior / 100.0), 0) + 3500.0
        elif self._current_stage_id == "treatment":
            interim_bill = round(pre_auth_approved * 0.92, 0)
            oop_est = round(interim_bill * (copay_senior / 100.0), 0) + 5200.0
        elif self._current_stage_id == "billing":
            interim_bill = round(pre_auth_approved * 1.25, 0)
            oop_est = round(interim_bill * (copay_senior / 100.0), 0) + 9800.0
        else: # discharge
            interim_bill = round(pre_auth_approved * 1.20, 0)
            oop_est = round(interim_bill * (copay_senior / 100.0), 0) + 9500.0

        room_tip = (
            "Any room category is permitted without sub-limit deduction (Clause 2.1)"
            if no_room_cap
            else f"Room capped at ₹{room_cap:,.0f}/day ({category}) to prevent proportionate deduction"
        )

        stages = [
            JourneyStageDetail(
                stage_id="admission",
                title="1. Emergency Admission & Pre-Auth",
                subtitle="Verify cashless eligibility, submit Form A, and obtain initial sanction",
                status="COMPLETED" if self._current_stage_id in ["treatment", "billing", "discharge"] else "IN_PROGRESS",
                metrics={
                    "Pre-Auth Sanction": f"₹{pre_auth_approved:,.0f}",
                    "TPA Status": f"Initial Cashless Sanction ({tpa_name})",
                    "Admission Mode": "Emergency Admission",
                    "Room Tariff Rule": f"Max ₹{room_cap:,.0f}/day" if not no_room_cap else "No Room Sub-limit"
                },
                checklist=[
                    StageChecklistItem(
                        id="chk-1",
                        task=f"Submit {policy.insurer_name} E-Card & Patient Aadhaar at Cashless Desk",
                        completed=True,
                        tip=f"Submitted within {notice_hours}-hr emergency window (Source: Page {policy.pre_auth.citation.page_number if policy.pre_auth.citation else 1})"
                    ),
                    StageChecklistItem(
                        id="chk-2",
                        task="Ensure Doctor's Admission Advice specifies diagnosis",
                        completed=True,
                        tip="Required to prevent queries on pre-existing condition exclusions"
                    ),
                    StageChecklistItem(
                        id="chk-3",
                        task=f"Confirm room tariff is within policy guidelines",
                        completed=True,
                        tip=room_tip
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-1",
                        stage="admission",
                        severity="SUCCESS",
                        title="Cashless Authorization Granted",
                        message=f"{tpa_name} issued initial cashless sanction of ₹{pre_auth_approved:,.0f} under {policy.policy_name}.",
                        timestamp="Admission + 1h 45m"
                    )
                ]
            ),
            JourneyStageDetail(
                stage_id="treatment",
                title="2. Treatment & Inpatient Monitoring",
                subtitle="Track daily charges, monitor room category, and trigger pre-auth enhancement",
                status="COMPLETED" if self._current_stage_id in ["billing", "discharge"] else ("IN_PROGRESS" if self._current_stage_id == "treatment" else "UPCOMING"),
                metrics={
                    "Current Interim Bill": f"₹{interim_bill:,.0f}",
                    "Sanction Utilisation": f"{(interim_bill / pre_auth_approved * 100):.1f}%",
                    "Days Inpatient": "Day 2 of 3",
                    "Consumables Accumulated": "₹3,400"
                },
                checklist=[
                    StageChecklistItem(
                        id="chk-4",
                        task="Verify daily doctor rounds charge against benchmark",
                        completed=self._current_stage_id in ["treatment", "billing", "discharge"],
                        tip="Physician visit capped under associated room charges"
                    ),
                    StageChecklistItem(
                        id="chk-5",
                        task=f"Request Pre-Auth Enhancement before bill exceeds ₹{pre_auth_approved:,.0f}",
                        completed=self._current_stage_id in ["billing", "discharge"],
                        tip="Prevents sudden cashless hold during intermediate procedures"
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-2",
                        stage="treatment",
                        severity="WARNING",
                        title="Enhancement Recommended",
                        message=f"Interim bill has reached 82% of ₹{pre_auth_approved:,.0f} sanction. Ask TPA desk to submit Enhancement Form.",
                        timestamp="Day 2, 14:30",
                        action_label="Trigger Enhancement Notice",
                        action_type="ENHANCEMENT"
                    )
                ]
            ),
            JourneyStageDetail(
                stage_id="billing",
                title="3. Billing & Discrepancy Audit",
                subtitle="Review draft bill, detect disallowed charges, and eliminate billing errors",
                status="COMPLETED" if self._current_stage_id == "discharge" else ("IN_PROGRESS" if self._current_stage_id == "billing" else "UPCOMING"),
                metrics={
                    "Hospital Draft Bill": f"₹{interim_bill:,.0f}",
                    "TPA Approved Cashless": f"₹{(interim_bill * 0.90):,.0f}",
                    "Disallowed Non-Medical": "₹8,500",
                    "CareWise Audit Savings": "₹4,500 (Duplicate syringe/glove charge removed)"
                },
                checklist=[
                    StageChecklistItem(
                        id="chk-6",
                        task="Inspect itemized pharmacy bill for non-covered items",
                        completed=self._current_stage_id == "discharge",
                        tip="Ensure hospital did not bill branded PPE kits outside IRDAI schedule"
                    ),
                    StageChecklistItem(
                        id="chk-7",
                        task="Cross-check OT consumable bill against surgery report",
                        completed=self._current_stage_id == "discharge",
                        tip="CareWise detected and resolved 1 duplicate dressing charge"
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-3",
                        stage="billing",
                        severity="INFO",
                        title="AI Bill Audit Complete",
                        message=f"Draft bill audited against {policy.insurer_name} IRDAI guidelines. Non-medical surcharges successfully contested.",
                        timestamp="Day 3, 10:15"
                    )
                ]
            ),
            JourneyStageDetail(
                stage_id="discharge",
                title="4. Discharge & Digital Claim Dossier",
                subtitle="Final cashless settlement confirmation and instant claim archive",
                status="IN_PROGRESS" if self._current_stage_id == "discharge" else "UPCOMING",
                metrics={
                    "Final Hospital Bill": f"₹{interim_bill:,.0f}",
                    "Cashless Paid by Insurer": f"₹{(interim_bill - oop_est):,.0f}",
                    "Caregiver Final Payment": f"₹{oop_est:,.0f} (Co-pay + non-medical)",
                    "Discharge Summary": "Signed & Archived"
                },
                checklist=[
                    StageChecklistItem(
                        id="chk-8",
                        task="Collect original Discharge Summary with doctor signature",
                        completed=self._current_stage_id == "discharge",
                        tip="Critical for post-hospitalisation 60-day medication claims"
                    ),
                    StageChecklistItem(
                        id="chk-9",
                        task="Obtain final Cashless Settlement Letter from TPA desk",
                        completed=self._current_stage_id == "discharge",
                        tip="Confirms zero outstanding balance with hospital"
                    ),
                    StageChecklistItem(
                        id="chk-10",
                        task="Download CareWise One-Click Claim & Care Dossier",
                        completed=self._current_stage_id == "discharge",
                        tip="Contains all receipts, diagnostic reports, and TPA authorization code"
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-4",
                        stage="discharge",
                        severity="SUCCESS",
                        title="Cashless Settlement Finalized",
                        message=f"Insurer has disbursed ₹{(interim_bill - oop_est):,.0f} directly to hospital. Zero debt remaining!",
                        timestamp="Day 3, 16:45"
                    )
                ]
            )
        ]

        active_alerts = []
        for s in stages:
            if s.stage_id == self._current_stage_id:
                active_alerts.extend(s.alerts)

        return JourneyStatusResponse(
            patient_name=self._patient_name,
            hospital_name=self._hospital_name,
            policy_name=policy.policy_name,
            admission_number=self._admission_number,
            current_stage_id=self._current_stage_id,
            pre_auth_approved_amount=pre_auth_approved,
            current_interim_bill=interim_bill,
            out_of_pocket_estimated=oop_est,
            stages=stages,
            active_alerts=active_alerts
        )

    def get_decision_guidance(
        self,
        policy_id: Optional[str] = None,
        selected_room: str = "twin_sharing",
        selected_procedure: str = "angioplasty",
        emergency_mode: bool = False
    ) -> Dict[str, Any]:
        """AI Recommendation & Justification Engine for Column 3 banner."""
        policy = self._resolve_policy(policy_id)
        room_cap = policy.room_limit.capped_amount_per_day or (policy.sum_insured * 0.01)
        no_room_cap = policy.room_limit.no_room_rent_capping
        category = policy.room_limit.allowed_room_category
        notice_hours = policy.pre_auth.emergency_window_hours
        copay_pct = policy.copay.senior_citizen_percentage

        # Evaluate proportionate deduction risk
        room_costs = {
            "twin_sharing": 6200.0,
            "single_private": 8500.0,
            "deluxe_suite": 14000.0
        }
        actual_tariff = room_costs.get(selected_room, 6200.0)
        is_breached = (not no_room_cap) and (actual_tariff > room_cap)

        if is_breached:
            penalty_ratio = (actual_tariff - room_cap) / actual_tariff
            estimated_penalty = round(110000.0 * penalty_ratio, 0)
            return {
                "headline": "⚠️ Proportionate Deduction Risk Active!",
                "justification": (
                    f"Selected room ({selected_room.replace('_', ' ').title()} @ ₹{actual_tariff:,.0f}/day) "
                    f"exceeds policy cap of ₹{room_cap:,.0f}/day. The insurer will proportionately cut "
                    f"doctor visit and OT surgeon charges by ~{penalty_ratio * 100:.0f}%, adding an extra ₹{estimated_penalty:,.0f} to your discharge bill."
                ),
                "priority": "CRITICAL",
                "action_label": "Switch to Twin Sharing (Safe)",
                "action_type": "SWITCH_ROOM",
                "recommended_room": "twin_sharing",
                "badge": "OVER-LIMIT DETECTED",
                "badge_color": "#f43f5e"
            }

        if emergency_mode:
            return {
                "headline": f"🚨 2 AM Emergency Protocol Active",
                "justification": (
                    f"Patient admitted via emergency. Hand over {policy.insurer_name} policy number to cashless desk. "
                    f"You have strictly {notice_hours} hours from admission to submit Pre-Auth Form A without penalty (Source: Page {policy.pre_auth.citation.page_number if policy.pre_auth.citation else 1})."
                ),
                "priority": "WARNING",
                "action_label": "Verify Pre-Auth Window",
                "action_type": "INTIMATE_PREAUTH",
                "badge": f"{notice_hours}H DEADLINE",
                "badge_color": "#f59e0b"
            }

        if copay_pct > 0:
            return {
                "headline": f"📋 Senior Co-Payment Condition Applies",
                "justification": (
                    f"For patient aged 61+, {policy.policy_name} enforces a mandatory {copay_pct:.0f}% co-payment "
                    f"on all admissible hospital charges (Source: Page {policy.copay.citation.page_number if policy.copay.citation else 2}). "
                    f"Room is safely within limit, avoiding additional proportionate penalties."
                ),
                "priority": "RECOMMENDED",
                "action_label": "Review Out-of-Pocket Breakdown",
                "action_type": "REVIEW_COPAY",
                "badge": f"{copay_pct:.0f}% CO-PAY",
                "badge_color": "#38bdf8"
            }

        return {
            "headline": "✅ Optimal Cashless Configuration",
            "justification": (
                f"Selected room tariff is within eligible policy parameters ({'No capping' if no_room_cap else f'Under ₹{room_cap:,.0f}/day cap'}). "
                f"Zero proportionate cuts will be applied to surgeon or OT fees. 100% cashless pre-auth path is active."
            ),
            "priority": "SUCCESS",
            "action_label": "Audit Final Bill Surcharges",
            "action_type": "AUDIT_BILL",
            "badge": "ZERO PENALTY",
            "badge_color": "#10b981"
        }

    def advance_stage(self, req: AdvanceJourneyRequest) -> JourneyStatusResponse:
        self._current_stage_id = req.target_stage_id
        return self.get_status()

    def generate_dossier(self, policy_id: Optional[str] = None) -> ClaimDossierResponse:
        policy = self._resolve_policy(policy_id)
        if not policy:
            raise ValueError("No policies available to derive dossier.")

        sum_insured = policy.sum_insured
        copay_senior = policy.copay.senior_citizen_percentage
        tpa_name = policy.empanelled_tpas[0] if policy.empanelled_tpas else "Medi Assist TPA"

        # Scale dynamically to policy sum insured and stage calculations
        pre_auth_approved = min(175000.0, max(50000.0, sum_insured * 0.15))
        total_bill = round(pre_auth_approved * 1.20, 0)
        copay_settled = round(total_bill * (copay_senior / 100.0), 0)
        non_medical_surcharges = 9500.0
        caregiver_paid = round(copay_settled + non_medical_surcharges, 0)
        cashless_sanctioned = round(total_bill - caregiver_paid, 0)

        # Dynamic TPA code from TPA initials and policy hash
        tpa_slug = re.sub(r'[^a-zA-Z0-9]', '', tpa_name.upper())[:6] or "TPA"
        policy_code = f"POL-{policy.id.upper()[:12]}-2026"
        tpa_submission_code = f"{tpa_slug}-{policy.id.upper()[:6]}-DIS"

        dossier_id = f"CW-DOS-{uuid.uuid4().hex[:8].upper()}"

        documents_checklist = [
            f"Original Discharge Summary with ICD-10 Diagnosis Codes ({self._hospital_name})",
            f"Itemized Hospital Final Bill (₹{total_bill:,.0f}) with Official Receipt Voucher",
            f"{tpa_name} Cashless Settlement Letter (Sanction: ₹{cashless_sanctioned:,.0f})",
            f"Pre-Auth Form A & Form B Endorsements under {policy.insurer_name}",
            "Diagnostic Laboratory & ECG/ECHO Medical Reports",
            "Implant Invoice & Barcode Sticker (Drug Eluting Stent / Consumables)"
        ]

        summary_text = (
            f"CareWise protected the family under {policy.policy_name} ({policy.insurer_name}) by preventing "
            f"proportionate deduction traps and actively auditing non-medical surcharges. Cashless settlement of "
            f"₹{cashless_sanctioned:,.0f} sanctioned with ₹{caregiver_paid:,.0f} out-of-pocket settled (including ₹{copay_settled:,.0f} co-pay)."
        )

        return ClaimDossierResponse(
            dossier_id=dossier_id,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            patient_name=self._patient_name,
            hospital_name=self._hospital_name,
            policy_number=policy_code,
            total_bill=total_bill,
            cashless_sanctioned=cashless_sanctioned,
            copay_settled=copay_settled,
            caregiver_paid=caregiver_paid,
            documents_checklist=documents_checklist,
            tpa_submission_code=tpa_submission_code,
            summary_text=summary_text
        )

    def generate_dossier_pdf(self, policy_id: Optional[str] = None) -> bytes:
        """Generate official CareWise Digital Claim Dossier PDF."""
        dossier = self.generate_dossier(policy_id=policy_id)
        return render_dossier_pdf(dossier)

    def trigger_caregiver_notification(
        self,
        policy_id: Optional[str] = None,
        phone_number: str = "+91 98765 43210",
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Trigger instant WhatsApp or SMS caregiver alert for stage updates & discharge dossier."""
        policy = self._resolve_policy(policy_id)
        stage_name = self._current_stage_id.title()
        msg_preview = (
            f"🏥 CareWise Update for {self._patient_name} at {self._hospital_name}: "
            f"Stage advanced to '{stage_name}'. Your cashless protection is verified under {policy.policy_name}."
        )
        return {
            "status": "SENT",
            "channel": channel,
            "recipient": phone_number,
            "stage": self._current_stage_id,
            "message_preview": msg_preview,
            "dispatched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "delivery_receipt": f"WA-MSG-{uuid.uuid4().hex[:10].upper()}"
        }


journey_service = JourneyService()

