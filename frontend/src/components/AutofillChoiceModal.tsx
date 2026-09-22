import React from 'react';
import { 
  FileText, 
  Zap, 
  BrainCircuit, 
  CheckCircle2, 
  X, 
  Sparkles,
  ShieldCheck,
  Clock
} from 'lucide-react';

interface AutofillChoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  fileName: string;
  fileSizeKb: number;
  onSelectQuick: () => void;
  onSelectDeep: () => void;
  isDeepLoading: boolean;
  pagesProcessed?: number;
}

export const AutofillChoiceModal: React.FC<AutofillChoiceModalProps> = ({
  isOpen,
  onClose,
  fileName,
  fileSizeKb,
  onSelectQuick,
  onSelectDeep,
  isDeepLoading,
  pagesProcessed = 1,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-card" 
        style={{ maxWidth: '580px', padding: '26px' }}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close-btn" onClick={onClose}>
          <X size={16} />
        </button>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '8px', borderRadius: '8px', color: '#0b3a72' }}>
            <FileText size={20} />
          </div>
          <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
              Select Auto-Fill & Extraction Mode
            </h3>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '2px' }}>
              Document: <strong style={{ color: 'var(--text-main)' }}>{fileName}</strong> ({fileSizeKb} KB • {pagesProcessed} {pagesProcessed === 1 ? 'Page' : 'Pages'})
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.82rem', color: '#334155', lineHeight: '1.5', margin: '14px 0 18px' }}>
          CareWise PyMuPDF text ingestion is complete. Choose how you would like AI to extract and structure policy schedules into your workbench:
        </p>

        {/* Options */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '20px' }}>
          
          {/* Quick Option */}
          <div 
            onClick={onSelectQuick}
            style={{
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              borderRadius: '10px',
              padding: '16px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#10b981')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.4)')}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#16a34a', fontWeight: 800, fontSize: '0.92rem', marginBottom: '6px' }}>
                <Zap size={16} />
                <span>Quick Auto-Fill</span>
              </div>
              <div style={{ fontSize: '0.76rem', color: '#64748b', lineHeight: '1.45' }}>
                Instant heuristic extraction for standard IRDAI formats. Immediately populates room rent, sum insured, and co-pay caps.
              </div>
            </div>
            
            <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', color: '#16a34a', fontWeight: 600 }}>
              <Clock size={12} /> Instant (&lt; 0.5s)
            </div>
          </div>

          {/* AI Deep Extraction Option */}
          <div 
            onClick={onSelectDeep}
            style={{
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid rgba(6, 182, 212, 0.5)',
              borderRadius: '10px',
              padding: '16px',
              cursor: isDeepLoading ? 'wait' : 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative',
              boxShadow: '0 0 15px rgba(6, 182, 212, 0.15)'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#0b3a72')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.5)')}
          >
            <div style={{ position: 'absolute', top: '-10px', right: '12px', background: 'linear-gradient(90deg, #0b3a72, #2563eb)', color: '#fff', fontSize: '0.66rem', fontWeight: 800, padding: '2px 8px', borderRadius: '10px' }}>
              RECOMMENDED
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#1d4ed8', fontWeight: 800, fontSize: '0.92rem', marginBottom: '6px' }}>
                <BrainCircuit size={16} />
                <span>AI Deep Extraction</span>
              </div>
              <div style={{ fontSize: '0.76rem', color: '#64748b', lineHeight: '1.45' }}>
                Multi-page LLM semantic reasoning. Deep extraction of sub-limits, cross-page waiting periods, exclusions & exact page citations.
              </div>
            </div>
            
            <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', color: '#1d4ed8', fontWeight: 600 }}>
              <Sparkles size={12} /> High-Precision Semantic Grounding
            </div>
          </div>
        </div>

        {/* Processing State if active */}
        {isDeepLoading && (
          <div style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '8px', padding: '12px', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#1d4ed8', fontWeight: 600 }}>
              <Sparkles size={16} className="spin" />
              <span>Running Deep LLM semantic extraction across {pagesProcessed} pages...</span>
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px' }}>
              Please wait while cross-page clauses and exact page citations are grounded.
            </div>
          </div>
        )}

        {/* Footer actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button 
            className="btn-header-action" 
            style={{ padding: '8px 16px', fontSize: '0.8rem' }}
            onClick={onClose}
          >
            Cancel
          </button>
          <button 
            className="btn-upload-main" 
            style={{ padding: '8px 18px', fontSize: '0.8rem' }}
            onClick={onSelectDeep}
            disabled={isDeepLoading}
          >
            <BrainCircuit size={15} />
            <span>{isDeepLoading ? 'Analyzing...' : 'Run AI Deep Extraction'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
