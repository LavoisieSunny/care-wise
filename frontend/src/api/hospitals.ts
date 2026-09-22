import api from './client';
import { Hospital } from '../types/hospital';

export interface HospitalFilterParams {
  policy_id?: string;
  locality?: string;
  max_distance_km?: number;
  specialty?: string;
  only_cashless?: boolean;
  emergency_mode?: boolean;
}

export const getHospitals = async (params: HospitalFilterParams = {}): Promise<{
  hospitals: Hospital[];
  total: number;
  nearest_cashless_id?: string;
}> => {
  const res = await api.get('/hospitals', { params });
  return res.data;
};
