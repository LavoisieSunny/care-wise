import api from './client';
import { PolicyDetails } from '../types/policy';

export const getPolicies = async (): Promise<PolicyDetails[]> => {
  const res = await api.get<{ policies: PolicyDetails[] }>('/policies');
  return res.data.policies;
};

export const getPolicy = async (policyId: string): Promise<PolicyDetails> => {
  const res = await api.get<PolicyDetails>(`/policies/${policyId}`);
  return res.data;
};

export const uploadPolicyPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/policies/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};
