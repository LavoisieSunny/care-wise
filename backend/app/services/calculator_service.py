from typing import List, Optional
from app.core.constants import PROCEDURE_BENCHMARKS, ROOM_TYPES
from app.schemas.calculator import (
    CostCalculationRequest,
    HospitalCostAnalysis,
    CostBreakdownItem,
    CompareHospitalsRequest,
    CompareHospitalsResponse
)
from app.services.policy_service import policy_service
from app.services.hospital_service import hospital_service

class CalculatorService:
    def calculate_single(self, req: CostCalculationRequest) -> HospitalCostAnalysis:
        policy = policy_service.get_policy(req.policy_id)
        if not policy:
            policy = policy_service.list_policies()[0]

        hospital = hospital_service.get_hospital(req.hospital_id)
        if not hospital:
            hospital = hospital_service.filter_hospitals(filter_req=None).hospitals[0]

        proc_info = PROCEDURE_BENCHMARKS.get(req.procedure_code, PROCEDURE_BENCHMARKS["angioplasty"])
        stay_days = req.stay_days or proc_info["avg_stay_days"]

        # Room tariff lookup
        room_rates = {
            "general": hospital.room_tariffs.general,
            "twin_sharing": hospital.room_tariffs.twin_sharing,
            "single_private": hospital.room_tariffs.single_private,
            "deluxe_suite": hospital.room_tariffs.deluxe_suite
        }
        room_rate = room_rates.get(req.room_type, hospital.room_tariffs.twin_sharing)
        room_label = ROOM_TYPES.get(req.room_type, ROOM_TYPES["twin_sharing"])["label"]

        # 1. Room cost
        total_room_cost = room_rate * stay_days

        # 2. Associated medical expenses (Surgeon, Anaesthesia, OT charges, Doctor rounds)
        associated_cost = proc_info["base_cost"] * proc_info["associated_medical_ratio"]
        procedure_implants_diagnostics = proc_info["base_cost"] * (1.0 - proc_info["associated_medical_ratio"] - proc_info["consumables_ratio"])
        
        # 3. Consumables cost
        consumables_cost = proc_info["base_cost"] * proc_info["consumables_ratio"]

        # Total hospital bill
        total_bill = total_room_cost + associated_cost + procedure_implants_diagnostics + consumables_cost

        # Policy Room Capping check
        policy_room_limit = policy.room_limit.capped_amount_per_day
        if policy.room_limit.no_room_rent_capping or policy_room_limit is None:
            policy_room_limit = room_rate # No cap

        proportionate_triggered = False
        proportionate_penalty = 0.0
        room_excess = 0.0

        if room_rate > policy_room_limit and policy.room_limit.proportionate_deduction_applies:
            proportionate_triggered = True
            room_excess = (room_rate - policy_room_limit) * stay_days
            ratio = policy_room_limit / room_rate
            # Insurer only covers ratio of associated medical costs
            proportionate_penalty = associated_cost * (1.0 - ratio)

        # Admissible associated cost after proportionate deduction
        admissible_associated = associated_cost - proportionate_penalty
        admissible_room = min(total_room_cost, policy_room_limit * stay_days)
        admissible_procedure = procedure_implants_diagnostics

        # Consumables coverage
        consumables_out_of_pocket = 0.0 if policy.has_consumables_rider else consumables_cost
        admissible_consumables = consumables_cost if policy.has_consumables_rider else 0.0

        admissible_subtotal = admissible_room + admissible_associated + admissible_procedure + admissible_consumables

        # Co-pay calculation
        copay_pct = policy.copay.senior_citizen_percentage if req.patient_age >= 60 else policy.copay.standard_percentage
        copay_deduction = (admissible_subtotal * (copay_pct / 100.0))

        # Check network cashless status
        is_cashless = hospital.network_status == "CASHLESS_NETWORK"

        if is_cashless:
            insurer_settlement = max(0.0, admissible_subtotal - copay_deduction)
            out_of_pocket = total_bill - insurer_settlement
        else:
            # Non-network: cashless denied; 100% out of pocket at hospital admission
            insurer_settlement = 0.0
            out_of_pocket = total_bill

        # Risk Classification
        risk_reasons = []
        if hospital.network_status == "NON_NETWORK":
            risk_tier = "NOT_ELIGIBLE"
            risk_reasons.append("Non-empanelled hospital: No cashless admission available. You must pay 100% upfront.")
        elif proportionate_triggered:
            risk_tier = "FINANCIAL_RISK"
            risk_reasons.append(
                f"Room Rent Cap Breached: Hospital charges ₹{room_rate:,.0f}/day vs policy limit of ₹{policy_room_limit:,.0f}/day."
            )
            risk_reasons.append(
                f"Proportionate Deduction Penalty: ₹{proportionate_penalty:,.0f} cut across Doctor fees & Operation Theatre charges!"
            )
        elif copay_pct > 0:
            risk_tier = "FINANCIAL_RISK"
            risk_reasons.append(f"{copay_pct:.0f}% Mandatory Senior Citizen Co-pay applies (₹{copay_deduction:,.0f}).")
        else:
            risk_tier = "RECOMMENDED"
            risk_reasons.append("100% Within policy room limits and cashless network.")
            risk_reasons.append("Zero proportionate deduction penalty.")

        if not policy.has_consumables_rider:
            risk_reasons.append(f"Non-medical items (gloves, PPE, kits) excluded: ~₹{consumables_cost:,.0f} out-of-pocket.")

        # Breakdown items
        breakdown = [
            CostBreakdownItem(
                category="Room Rent & Nursing",
                hospital_charged=total_room_cost,
                insurer_covered=admissible_room,
                caregiver_out_of_pocket=room_excess,
                notes=f"{stay_days} days @ ₹{room_rate:,.0f}/day (Policy Cap: ₹{policy_room_limit:,.0f}/day)"
            ),
            CostBreakdownItem(
                category="Associated Medical Fees (Surgeon, Anaesthesia, OT)",
                hospital_charged=associated_cost,
                insurer_covered=admissible_associated,
                caregiver_out_of_pocket=proportionate_penalty,
                notes=f"Proportionate cut of ₹{proportionate_penalty:,.0f} due to room category upgrade" if proportionate_triggered else "Fully eligible (no proportionate penalty)"
            ),
            CostBreakdownItem(
                category="Procedure, Implants & Diagnostics",
                hospital_charged=procedure_implants_diagnostics,
                insurer_covered=procedure_implants_diagnostics,
                caregiver_out_of_pocket=0.0,
                notes="100% covered under base surgical benefit"
            ),
            CostBreakdownItem(
                category="Non-Medical Items & Consumables",
                hospital_charged=consumables_cost,
                insurer_covered=admissible_consumables,
                caregiver_out_of_pocket=consumables_out_of_pocket,
                notes="Covered under Plus Rider" if policy.has_consumables_rider else "IRDAI List I non-payable items (gloves, PPE, sanitizers)"
            )
        ]

        if copay_pct > 0:
            breakdown.append(
                CostBreakdownItem(
                    category=f"Mandatory Co-Payment ({copay_pct:.0f}%)",
                    hospital_charged=0.0,
                    insurer_covered=0.0,
                    caregiver_out_of_pocket=copay_deduction,
                    notes=f"Senior Citizen age clause ({req.patient_age} yrs)"
                )
            )

        return HospitalCostAnalysis(
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            network_status=hospital.network_status,
            procedure_name=proc_info["name"],
            room_type=req.room_type,
            room_type_label=room_label,
            stay_days=stay_days,
            daily_room_charge=room_rate,
            policy_room_limit_daily=policy_room_limit,
            proportionate_deduction_triggered=proportionate_triggered,
            proportionate_deduction_penalty=proportionate_penalty,
            copay_percentage=copay_pct,
            copay_amount=copay_deduction,
            non_medical_consumables=consumables_out_of_pocket,
            total_bill=round(total_bill),
            insurer_settlement=round(insurer_settlement),
            estimated_out_of_pocket=round(out_of_pocket),
            risk_tier=risk_tier,
            risk_reasons=risk_reasons,
            breakdown=breakdown
        )

    def compare_multiple(self, req: CompareHospitalsRequest) -> CompareHospitalsResponse:
        policy = policy_service.get_policy(req.policy_id) or policy_service.list_policies()[0]
        proc_info = PROCEDURE_BENCHMARKS.get(req.procedure_code, PROCEDURE_BENCHMARKS["angioplasty"])

        analyses: List[HospitalCostAnalysis] = []
        for hid in req.hospital_ids:
            single_req = CostCalculationRequest(
                policy_id=policy.id,
                hospital_id=hid,
                procedure_code=req.procedure_code,
                room_type=req.room_type,
                stay_days=req.stay_days,
                patient_age=req.patient_age
            )
            analyses.append(self.calculate_single(single_req))

        # Best hospital recommendation: lowest out of pocket with CASHLESS_NETWORK
        valid_cashless = [a for a in analyses if a.network_status == "CASHLESS_NETWORK"]
        if valid_cashless:
            recommended = min(valid_cashless, key=lambda a: a.estimated_out_of_pocket)
        else:
            recommended = analyses[0]

        max_oop = max(a.estimated_out_of_pocket for a in analyses) if analyses else 0.0
        savings = max(0.0, max_oop - recommended.estimated_out_of_pocket)

        return CompareHospitalsResponse(
            policy_id=policy.id,
            policy_name=policy.policy_name,
            procedure_name=proc_info["name"],
            comparisons=analyses,
            recommended_hospital_id=recommended.hospital_id,
            savings_vs_riskiest=savings
        )

calculator_service = CalculatorService()
