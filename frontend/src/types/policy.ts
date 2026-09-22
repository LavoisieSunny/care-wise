export interface ClauseCitation {
  clause_id: string;
  section: string;
  page_number: number;
  clause_title: string;
  exact_text: string;
  tag: string;
  confidence?: number;
}

export interface PolicyRoomLimit {
  capped_amount_per_day: number | null;
  percentage_of_sum_insured: number | null;
  no_room_rent_capping: boolean;
  allowed_room_category: string;
  proportionate_deduction_applies: boolean;
  citation?: ClauseCitation;
}

export interface PolicyCoPay {
  standard_percentage: number;
  senior_citizen_percentage: number;
  zone_based_copay: number;
  citation?: ClauseCitation;
}

export interface PolicyPreAuth {
  emergency_window_hours: number;
  planned_window_hours: number;
  citation?: ClauseCitation;
}

export interface WaitingPeriod {
  type: string;
  duration: string;
  description: string;
  page: number;
}

export interface PolicyDetails {
  id: string;
  insurer_name: string;
  policy_name: string;
  policy_type: string;
  sum_insured: number;
  room_limit: PolicyRoomLimit;
  icu_limit_per_day?: number;
  copay: PolicyCoPay;
  pre_auth: PolicyPreAuth;
  has_consumables_rider: boolean;
  empanelled_tpas: string[];
  waiting_periods: WaitingPeriod[];
  key_exclusions: string[];
  all_citations: ClauseCitation[];
  raw_text_pages?: Record<string, string>;
}

export interface PolicyUploadResponse {
  success: boolean;
  message: string;
  policy: PolicyDetails;
  pages_processed: number;
  confidence_score: number;
  upload_id?: string;
  extraction_mode?: string;
}

