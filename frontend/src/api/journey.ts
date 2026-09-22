import api from './client';
import { JourneyStatusResponse, ClaimDossierResponse } from '../types/journey';

export interface DecisionGuidance {
  headline: string;
  justification: string;
  priority: 'CRITICAL' | 'WARNING' | 'RECOMMENDED' | 'SUCCESS';
  action_label: string;
  action_type: string;
  recommended_room?: string;
  badge: string;
  badge_color: string;
}

export const getJourneyStatus = async (policyId?: string): Promise<JourneyStatusResponse> => {
  const url = policyId ? `/journey/status?policy_id=${policyId}` : '/journey/status';
  const res = await api.get<JourneyStatusResponse>(url);
  return res.data;
};

export const getJourneyGuidance = async (params: {
  policy_id?: string;
  room_type?: string;
  procedure?: string;
  emergency_mode?: boolean;
}): Promise<DecisionGuidance> => {
  const query = new URLSearchParams();
  if (params.policy_id) query.append('policy_id', params.policy_id);
  if (params.room_type) query.append('room_type', params.room_type);
  if (params.procedure) query.append('procedure', params.procedure);
  if (params.emergency_mode !== undefined) query.append('emergency_mode', String(params.emergency_mode));
  
  const res = await api.get<DecisionGuidance>(`/journey/guidance?${query.toString()}`);
  return res.data;
};

export const advanceJourney = async (targetStageId: string): Promise<JourneyStatusResponse> => {
  const res = await api.post<JourneyStatusResponse>('/journey/advance', { target_stage_id: targetStageId });
  return res.data;
};

export const generateDossier = async (policyId?: string): Promise<ClaimDossierResponse> => {
  const url = policyId ? `/journey/dossier?policy_id=${policyId}` : '/journey/dossier';
  const res = await api.post<ClaimDossierResponse>(url);
  return res.data;
};


export const generateSOS = async (params: {
  patient_name: string;
  hospital_name: string;
  emergency_contact: string;
  policy_name: string;
  room_cap: string;
  tpa_name: string;
  pre_auth_status: string;
}) => {
  const res = await api.post('/sos/generate', params);
  return res.data;
};
