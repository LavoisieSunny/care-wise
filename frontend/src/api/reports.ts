import api from './client';
import { CompareHospitalsResponse } from '../types/calculator';

export interface ClaimReadinessReport {
  report_id: string;
  generated_at: string;
  policy_name: string;
  ai_summary: string;
  recommended_hospital: string;
  savings_vs_riskiest: number;
  comparisons: any[];
}

export const generateClaimReadinessReport = async (
  policyId: string,
  comparison: CompareHospitalsResponse
): Promise<ClaimReadinessReport> => {
  const res = await api.post<ClaimReadinessReport>('/reports/claim-readiness', {
    policy_id: policyId,
    comparison,
  });
  return res.data;
};

export const downloadClaimReadinessPdf = async (
  policyId: string,
  comparison: CompareHospitalsResponse
): Promise<void> => {
  const res = await api.post(
    '/reports/claim-readiness/pdf',
    { policy_id: policyId, comparison },
    { responseType: 'blob' }
  );
  const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'CareWise_Claim_Readiness_Report.pdf');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
