export interface JourneyAlert {
  id: string;
  stage: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL' | 'SUCCESS';
  title: string;
  message: string;
  timestamp: string;
  action_label?: string;
  action_type?: string;
}

export interface StageChecklistItem {
  id: string;
  task: string;
  completed: boolean;
  required: boolean;
  tip: string;
}

export interface JourneyStageDetail {
  stage_id: 'admission' | 'treatment' | 'billing' | 'discharge';
  title: string;
  subtitle: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'UPCOMING';
  metrics: Record<string, string>;
  checklist: StageChecklistItem[];
  alerts: JourneyAlert[];
}

export interface JourneyStatusResponse {
  patient_name: string;
  hospital_name: string;
  policy_name: string;
  admission_number: string;
  current_stage_id: 'admission' | 'treatment' | 'billing' | 'discharge';
  pre_auth_approved_amount: number;
  current_interim_bill: number;
  out_of_pocket_estimated: number;
  stages: JourneyStageDetail[];
  active_alerts: JourneyAlert[];
}

export interface ClaimDossierResponse {
  dossier_id: string;
  generated_at: string;
  patient_name: string;
  hospital_name: string;
  policy_number: string;
  total_bill: number;
  cashless_sanctioned: number;
  copay_settled: number;
  caregiver_paid: number;
  documents_checklist: string[];
  tpa_submission_code: string;
  summary_text: string;
}
