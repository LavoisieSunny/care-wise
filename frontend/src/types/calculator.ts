export interface CostBreakdownItem {
  category: string;
  hospital_charged: number;
  insurer_covered: number;
  caregiver_out_of_pocket: number;
  notes: string;
}

export interface HospitalCostAnalysis {
  hospital_id: string;
  hospital_name: string;
  network_status: 'CASHLESS_NETWORK' | 'REIMBURSEMENT_ONLY' | 'NON_NETWORK';
  procedure_name: string;
  room_type: string;
  room_type_label: string;
  stay_days: number;
  daily_room_charge: number;
  policy_room_limit_daily: number;
  proportionate_deduction_triggered: boolean;
  proportionate_deduction_penalty: number;
  copay_percentage: number;
  copay_amount: number;
  non_medical_consumables: number;
  total_bill: number;
  insurer_settlement: number;
  estimated_out_of_pocket: number;
  risk_tier: 'RECOMMENDED' | 'FINANCIAL_RISK' | 'NOT_ELIGIBLE';
  risk_reasons: string[];
  breakdown: CostBreakdownItem[];
}

export interface CompareHospitalsResponse {
  policy_id: string;
  policy_name: string;
  procedure_name: string;
  comparisons: HospitalCostAnalysis[];
  recommended_hospital_id: string;
  savings_vs_riskiest: number;
}
