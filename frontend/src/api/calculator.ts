import api from './client';
import { HospitalCostAnalysis, CompareHospitalsResponse } from '../types/calculator';

export interface CompareRequestParams {
  policy_id: string;
  hospital_ids: string[];
  procedure_code: string;
  room_type?: string;
  stay_days?: number;
  patient_age?: number;
}

export const compareHospitals = async (params: CompareRequestParams): Promise<CompareHospitalsResponse> => {
  const res = await api.post<CompareHospitalsResponse>('/calculator/compare', params);
  return res.data;
};

export const simulateCost = async (params: {
  policy_id: string;
  hospital_id: string;
  procedure_code: string;
  room_type: string;
  stay_days?: number;
  patient_age?: number;
}): Promise<HospitalCostAnalysis> => {
  const res = await api.post<HospitalCostAnalysis>('/calculator/simulate', params);
  return res.data;
};
