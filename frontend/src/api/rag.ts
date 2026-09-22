import api from './client';
import { GroundedAnswerResponse } from '../types/rag';

export const queryRAG = async (params: {
  policy_id: string;
  query: string;
  hospital_name?: string;
  procedure_name?: string;
  language?: string;
}): Promise<GroundedAnswerResponse> => {
  const res = await api.post<GroundedAnswerResponse>('/rag/query', params);
  return res.data;
};
