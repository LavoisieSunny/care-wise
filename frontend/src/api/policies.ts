import api from './client';
import { PolicyDetails, PolicyUploadResponse } from '../types/policy';

export const getPolicies = async (): Promise<PolicyDetails[]> => {
  const res = await api.get<{ policies: PolicyDetails[] }>('/policies');
  return res.data.policies;
};

export const getPolicy = async (policyId: string): Promise<PolicyDetails> => {
  const res = await api.get<PolicyDetails>(`/policies/${policyId}`);
  return res.data;
};

export const uploadPolicyPDF = async (file: File, mode: 'quick' | 'ai' = 'quick'): Promise<PolicyUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post<PolicyUploadResponse>(`/policies/upload?mode=${mode}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const uploadPolicyDeep = async (uploadId: string): Promise<PolicyUploadResponse> => {
  const res = await api.post<PolicyUploadResponse>(`/policies/upload/deep?upload_id=${uploadId}`);
  return res.data;
};

export const getPolicyAISummary = async (policyId: string): Promise<{ summary: string }> => {
  const res = await api.get<{ policy_id: string; summary: string }>(`/policies/${policyId}/summary`);
  return res.data;
};

