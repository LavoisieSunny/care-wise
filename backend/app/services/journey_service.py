import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.schemas.journey import (
    JourneyStatusResponse,
    JourneyStageDetail,
    JourneyAlert,
    StageChecklistItem,
    AdvanceJourneyRequest,
    ClaimDossierResponse
)

class JourneyService:
    def __init__(self):
        self._current_stage_id = "admission"
        self._patient_name = "Ramesh Sharma (Age 58)"
        self._hospital_name = "Sanjeevani Multispeciality Hospital"
        self._policy_name = "Star Health Family Health Optima (₹5,00,000 SI)"
        self._admission_number = "ADM-2026-89410"
        self._pre_auth_approved = 75000.0
        self._current_interim_bill = 62000.0
        self._estimated_oop = 4500.0

    def get_status(self) -> JourneyStatusResponse:
        stages = [
            JourneyStageDetail(
                stage_id="admission",
                title="1. Emergency Admission & Pre-Auth",
                subtitle="Verify cashless eligibility, submit Form A, and obtain initial sanction",
                status="COMPLETED" if self._current_stage_id in ["treatment", "billing", "discharge"] else "IN_PROGRESS",
                metrics={
                    "Pre-Auth Sanction": f"₹{self._pre_auth_approved:,.0f}",
                    "TPA Status": "Initial Approval Granted (Medi Assist)",
                    "Admission Mode": "2 AM Emergency",
                    "Room Allocated": "Standard Twin Sharing (₹4,200/day)"
                },
                checklist=[
                    StageChecklistItem(
                        id="chk-1",
                        task="Submit Policy E-Card & Patient Aadhaar at Cashless Desk",
                        completed=True,
                        tip="Submitted within 24-hr emergency window (Clause SEC-7.4)"
                    ),
                    StageChecklistItem(
                        id="chk-2",
                        task="Ensure Doctor's Admission Advice specifies diagnosis",
                        completed=True,
                        tip="Required to prevent queries on pre-existing condition exclusions"
                    ),
                    StageChecklistItem(
                        id="chk-3",
                        task="Confirm room tariff is within ₹5,000/day policy cap",
                        completed=True,
                        tip="Twin sharing chosen at ₹4,200/day avoids proportionate deduction"
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-1",
                        stage="admission",
                        severity="SUCCESS",
                        title="Pre-Authorization Approved",
                        message="Medi Assist TPA has issued initial cashless authorization of ₹75,000. Admission processed under cashless network.",
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
                    "Current Interim Bill": f"₹{self._current_interim_bill:,.0f}",
                    "Sanction Utilisation": f"{(self._current_interim_bill / self._pre_auth_approved * 100):.1f}%",
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
                        task="Request Pre-Auth Enhancement before bill exceeds ₹75,000",
                        completed=self._current_stage_id in ["billing", "discharge"],
                        tip="Prevents sudden cashless hold during catheterization/stenting"
                    )
                ],
                alerts=[
                    JourneyAlert(
                        id="alt-2",
                        stage="treatment",
                        severity="WARNING",
                        title="Enhancement Required Soon",
                        message="Interim bill has reached 82% of initial pre-auth. CareWise recommends asking hospital desk to submit Enhancement Form.",
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
                    "Hospital Draft Bill": "₹1,85,000",
                    "TPA Approved Cashless": "₹1,68,500",
                    "Disallowed Non-Medical": "₹12,000",
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
                        message="Draft bill audited against Star Health IRDAI guidelines. ₹4,500 in unjustified consumable surcharges successfully contested.",
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
                    "Final Hospital Bill": "₹1,80,500",
                    "Cashless Paid by Insurer": "₹1,71,000",
                    "Caregiver Final Payment": "₹9,500 (Non-medical items only)",
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
                        message="Insurer has disbursed ₹1,71,000 directly to hospital. Total caregiver out-of-pocket kept under ₹10,000!",
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
            policy_name=self._policy_name,
            admission_number=self._admission_number,
            current_stage_id=self._current_stage_id,
            pre_auth_approved_amount=self._pre_auth_approved,
            current_interim_bill=self._current_interim_bill,
            out_of_pocket_estimated=self._estimated_oop,
            stages=stages,
            active_alerts=active_alerts
        )

    def advance_stage(self, req: AdvanceJourneyRequest) -> JourneyStatusResponse:
        self._current_stage_id = req.target_stage_id
        if req.target_stage_id == "treatment":
            self._current_interim_bill = 68000.0
        elif req.target_stage_id == "billing":
            self._current_interim_bill = 185000.0
            self._pre_auth_approved = 168500.0
        elif req.target_stage_id == "discharge":
            self._current_interim_bill = 180500.0
            self._pre_auth_approved = 171000.0
            self._estimated_oop = 9500.0
        return self.get_status()

    def generate_dossier(self) -> ClaimDossierResponse:
        return ClaimDossierResponse(
            dossier_id=f"CW-DOS-{uuid.uuid4().hex[:8].upper()}",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            patient_name=self._patient_name,
            hospital_name=self._hospital_name,
            policy_number="STAR-FHO-2024-99812",
            total_bill=180500.0,
            cashless_sanctioned=171000.0,
            copay_settled=0.0,
            caregiver_paid=9500.0,
            documents_checklist=[
                "Original Discharge Summary with ICD-10 Diagnosis Codes",
                "Itemized Hospital Final Bill with Receipt Voucher",
                "TPA Cashless Settlement Letter (Ref #MA-992182)",
                "Pre-Auth Form A & Form B Endorsements",
                "Diagnostic Laboratory & ECG/ECHO Reports",
                "Implant Invoice & Barcode Sticker (Drug Eluting Stent)"
            ],
            tpa_submission_code="TPA-MED-889921",
            summary_text="CareWise protected the family from a potential ₹75,000 proportionate deduction bill shock by recommending a Twin Sharing room and actively auditing non-medical charges."
        )

journey_service = JourneyService()
