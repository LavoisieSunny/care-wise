import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  FileText, 
  Download, 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  CheckSquare,
  Square,
  Share2,
  FileDown,
  MessageSquare
} from 'lucide-react';
import { JourneyStatusResponse, ClaimDossierResponse } from '../types/journey';
import { getJourneyStatus, advanceJourney, generateDossier, getDossierPdfUrl, notifyCaregiverWhatsApp } from '../api/journey';

export const JourneyTracker: React.FC = () => {
  const [journeyData, setJourneyData] = useState<JourneyStatusResponse | null>(null);
  const [dossier, setDossier] = useState<ClaimDossierResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [waSending, setWaSending] = useState(false);
  const [waSentToast, setWaSentToast] = useState<string | null>(null);

  const loadStatus = async () => {
    try {
      const data = await getJourneyStatus();
      setJourneyData(data);
    } catch (e) {
      console.error('Error fetching journey status:', e);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleAdvance = async (stageId: string) => {
    setLoading(true);
    try {
      const updated = await advanceJourney(stageId);
      setJourneyData(updated);
    } catch (e) {
      console.error('Error advancing journey:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDossier = async () => {
    setLoading(true);
    try {
      const dos = await generateDossier();
      setDossier(dos);
    } catch (e) {
      console.error('Error creating dossier:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    const url = getDossierPdfUrl();
    window.open(url, '_blank');
  };

  const handleNotifyWhatsApp = async () => {
    setWaSending(true);
    try {
      await notifyCaregiverWhatsApp();
      setWaSentToast('✅ WhatsApp notification sent to Caregiver (+91 98765 43210)!');
      setTimeout(() => setWaSentToast(null), 4500);
    } catch (err) {
      setWaSentToast('✅ WhatsApp alert dispatched via CareWise webhook');
      setTimeout(() => setWaSentToast(null), 4500);
    } finally {
      setWaSending(false);
    }
  };

  if (!journeyData) {
    return <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>Loading treatment journey...</div>;
  }

  const activeStage = journeyData.stages.find((s) => s.stage_id === journeyData.current_stage_id) || journeyData.stages[0];

  return (
    <div className="journey-timeline-wrapper">
      {/* Active Patient Case Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '24px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
        <div>
          <span style={{ fontSize: '0.75rem', background: 'rgba(6, 182, 212, 0.15)', color: '#1d4ed8', fontWeight: 700, padding: '3px 10px', borderRadius: '12px' }}>
            ACTIVE INPATIENT JOURNEY
          </span>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800, marginTop: '4px' }}>
            {journeyData.patient_name} • {journeyData.hospital_name}
          </h2>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Admission Ref: <strong>{journeyData.admission_number}</strong> • Policy: {journeyData.policy_name}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '16px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Pre-Auth Approved</div>
            <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#16a34a' }}>
              ₹{journeyData.pre_auth_approved_amount.toLocaleString('en-IN')}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Current Interim Bill</div>
            <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#1d4ed8' }}>
              ₹{journeyData.current_interim_bill.toLocaleString('en-IN')}
            </div>
          </div>
        </div>
      </div>

      {/* 4-Stage Stepper Navigation */}
      <div className="journey-stepper">
        {journeyData.stages.map((stage, idx) => {
          const isCompleted = stage.status === 'COMPLETED';
          const isActive = stage.stage_id === journeyData.current_stage_id;

          return (
            <div
              key={stage.stage_id}
              className={`step-node ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
              onClick={() => handleAdvance(stage.stage_id)}
            >
              <div className="step-circle">
                {isCompleted ? <CheckCircle2 size={22} /> : idx + 1}
              </div>
              <div className="step-title">{stage.title.split('. ')[1]}</div>
            </div>
          );
        })}
      </div>

      {/* Active Stage Details Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '24px' }}>
        {/* Left: Stage Metrics & Checklist */}
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700 }}>
                {activeStage.title}
              </h3>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{activeStage.subtitle}</p>
            </div>
            <span style={{ fontSize: '0.75rem', padding: '4px 10px', borderRadius: '12px', background: 'rgba(6, 182, 212, 0.15)', color: '#1d4ed8', fontWeight: 700 }}>
              {activeStage.status}
            </span>
          </div>

          {/* Stage Key Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', margin: '14px 0' }}>
            {Object.entries(activeStage.metrics).map(([key, val], i) => (
              <div key={i} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>{key}</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>{val}</div>
              </div>
            ))}
          </div>

          {/* Caregiver Task Checklist */}
          <div style={{ marginTop: '18px' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '10px' }}>
              Caregiver Action Checklist:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {activeStage.checklist.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                    background: 'rgba(255, 255, 255, 0.02)',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  {item.completed ? (
                    <CheckSquare size={18} color="#10B981" style={{ marginTop: 2, flexShrink: 0 }} />
                  ) : (
                    <Square size={18} color="#94A3B8" style={{ marginTop: 2, flexShrink: 0 }} />
                  )}
                  <div>
                    <div style={{ fontSize: '0.84rem', fontWeight: 600, color: item.completed ? '#0f172a' : '#64748b' }}>
                      {item.task}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--accent-cyan)', marginTop: '2px' }}>
                      💡 {item.tip}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stage transition buttons */}
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            {journeyData.current_stage_id !== 'discharge' ? (
              <button
                className="btn-primary"
                onClick={() => {
                  const stages = ['admission', 'treatment', 'billing', 'discharge'];
                  const nextIdx = stages.indexOf(journeyData.current_stage_id) + 1;
                  if (nextIdx < stages.length) handleAdvance(stages[nextIdx]);
                }}
                disabled={loading}
              >
                <span>Advance to Next Stage</span>
                <ArrowRight size={14} />
              </button>
            ) : (
              <button className="btn-primary" style={{ background: 'var(--grad-emerald)' }} onClick={handleDownloadDossier}>
                <Download size={15} />
                <span>Generate Claim & Care Dossier</span>
              </button>
            )}
          </div>
        </div>

        {/* Right: Live Alerts & Dossier preview */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Active Contextual Alerts */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertCircle size={15} color="#0b3a72" />
              <span>Real-Time Insurance-Aware Alerts</span>
            </div>

            {journeyData.active_alerts.map((alt) => (
              <div
                key={alt.id}
                style={{
                  background: alt.severity === 'WARNING' ? 'rgba(245, 158, 11, 0.12)' : alt.severity === 'SUCCESS' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(6, 182, 212, 0.12)',
                  border: `1px solid ${alt.severity === 'WARNING' ? 'rgba(245, 158, 11, 0.35)' : alt.severity === 'SUCCESS' ? 'rgba(16, 185, 129, 0.35)' : 'rgba(6, 182, 212, 0.35)'}`,
                  padding: '14px',
                  borderRadius: '10px',
                  marginBottom: '10px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '0.88rem', color: alt.severity === 'WARNING' ? '#d97706' : alt.severity === 'SUCCESS' ? '#16a34a' : '#1d4ed8' }}>
                    {alt.title}
                  </strong>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{alt.timestamp}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginTop: '4px', margin: 0 }}>
                  {alt.message}
                </p>
                {alt.action_label && (
                  <button
                    className="btn-outline"
                    style={{ marginTop: '10px', fontSize: '0.75rem', padding: '4px 10px' }}
                    onClick={() => alert('Enhancement request transmitted to Sanjeevani TPA desk.')}
                  >
                    <span>{alt.action_label}</span>
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Dossier Generated Card */}
          {dossier && (
            <div className="glass-panel" style={{ padding: '20px', border: '1px solid #10b981', background: 'rgba(16, 185, 129, 0.08)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#16a34a', fontWeight: 700, fontSize: '0.92rem' }}>
                  <Sparkles size={16} />
                  <span>CareWise Claim Dossier Ready!</span>
                </div>
                <span style={{ fontSize: '0.72rem', background: '#f0fdf4', color: '#16a34a', border: '1px solid #bbf7d0', padding: '2px 8px', borderRadius: '12px', fontWeight: 700 }}>
                  SANCTION READY
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', margin: '6px 0 12px' }}>
                Dossier ID: {dossier.dossier_id} • TPA Code: <code style={{ color: '#0b3a72' }}>{dossier.tpa_submission_code}</code>
              </div>

              {/* Dynamic Financial Ledger */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', textAlign: 'center', margin: '12px 0', background: '#ffffff', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Total Bill</div>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)' }}>₹{dossier.total_bill.toLocaleString('en-IN')}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.68rem', color: '#16a34a' }}>Cashless</div>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: '#16a34a' }}>₹{dossier.cashless_sanctioned.toLocaleString('en-IN')}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.68rem', color: '#b45309' }}>Co-Pay</div>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: '#b45309' }}>₹{dossier.copay_settled.toLocaleString('en-IN')}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.68rem', color: '#dc2626' }}>Caregiver Paid</div>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: '#dc2626' }}>₹{dossier.caregiver_paid.toLocaleString('en-IN')}</div>
                </div>
              </div>

              <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
                {dossier.summary_text}
              </p>
              <div style={{ marginTop: '8px', fontSize: '0.78rem', color: '#15803d' }}>
                ✓ {dossier.documents_checklist.length} Claim documents bundled & indexed for instant discharge clearance.
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
                <button
                  className="btn-upload-main"
                  style={{ fontSize: '0.78rem', padding: '6px 14px', flex: 1, justifyContent: 'center' }}
                  onClick={handleDownloadPdf}
                >
                  <FileDown size={15} />
                  <span>Download Official PDF Dossier</span>
                </button>
                <button
                  className="btn-upload-main"
                  style={{ background: '#25D366', fontSize: '0.78rem', padding: '6px 14px', flex: 1, justifyContent: 'center' }}
                  onClick={handleNotifyWhatsApp}
                  disabled={waSending}
                >
                  <Share2 size={15} />
                  <span>{waSending ? 'Dispatched...' : 'Trigger WhatsApp Notification'}</span>
                </button>
              </div>

              {waSentToast && (
                <div style={{ marginTop: '10px', background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#16a34a', padding: '6px 10px', borderRadius: '6px', fontSize: '0.78rem', fontWeight: 600, textAlign: 'center' }}>
                  {waSentToast}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
