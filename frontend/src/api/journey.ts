import api from './client';
import { JourneyStatusResponse, ClaimDossierResponse } from '../types/journey';

export const getJourneyStatus = async (): Promise<JourneyStatusResponse> => {
  const res = await api.get<JourneyStatusResponse>('/journey/status');
  return res.data;
};

export const advanceJourney = async (targetStageId: string): Promise<JourneyStatusResponse> => {
  const res = await api.post<JourneyStatusResponse>('/journey/advance', { target_stage_id: targetStageId });
  return res.data;
};

export const generateDossier = async (): Promise<ClaimDossierResponse> => {
  const res = await api.post<ClaimDossierResponse>('/journey/dossier');
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
