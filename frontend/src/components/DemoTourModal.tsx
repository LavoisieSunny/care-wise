import React, { useState } from 'react';
import { X, Award, ChevronRight, ChevronLeft, Check, Sparkles, Target } from 'lucide-react';

interface DemoTourModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchTab: (tabIndex: number) => void;
}

export const DemoTourModal: React.FC<DemoTourModalProps> = ({
  isOpen,
  onClose,
  onSwitchTab,
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  if (!isOpen) return null;

  const tourSteps = [
    {
      title: '1. The 2 AM Dilemma: Caregivers Make Decisions Blind',
      category: 'PROBLEM STATEMENT',
      tabIndex: 0,
      description:
        'During medical emergencies, caregivers — not patients — make high-stakes financial decisions at 2 AM with no clear view of policy limits, cashless empanelment, or hidden proportionate deductions.',
      keyHighlight:
        'CareWise is the first caregiver-first platform designed to turn midnight panic into confident, informed choices.',
    },
    {
      title: '2. Grounded RAG AI: Citations, Not Hallucinations',
      category: 'TECHNOLOGY INNOVATION',
      tabIndex: 0,
      description:
        'CareWise extracts complex policy documents and indexes every clause. Inquiries are answered using grounded retrieval, with citations linking back to the exact page and clause.',
      keyHighlight:
        'Click any extracted badge or chat answer to jump straight into the highlighted policy document view.',
    },
    {
      title: '3. Real-Time Hospital Discovery & 2 AM Mode',
      category: 'HOSPITAL NETWORK',
      tabIndex: 1,
      description:
        'Filters nearby hospitals by emergency ICU bed availability, distance, medical specialty, and active cashless TPA empanelment.',
      keyHighlight:
        'Toggle the "🚨 2 AM Emergency Mode" in the header to instantly filter for the nearest 24/7 cashless hospital with available ICU beds.',
    },
    {
      title: '4. The Proportionate Deduction Trap Exposed',
      category: 'FINANCIAL CLARITY',
      tabIndex: 2,
      description:
        'In India, choosing a room above policy limits doesn’t just cost extra room rent — insurers proportionately slash doctor fees, surgery, and OT charges! CareWise computes this exact penalty in real time.',
      keyHighlight:
        'Test switching from "Twin Sharing" to "Deluxe Suite" to see how out-of-pocket costs jump by ₹75,000+ due to proportionate deductions!',
    },
    {
      title: '5. End-to-End Treatment Journey & Claim Dossier',
      category: 'CONTINUOUS SUPPORT',
      tabIndex: 3,
      description:
        'CareWise accompanies the caregiver from admission pre-authorization through inpatient treatment, interim bill audits, and final discharge.',
      keyHighlight:
        'Advance through the 4 stages to experience AI billing discrepancy detection and generate a one-click CareWise Claim Dossier.',
    },
  ];

  const step = tourSteps[currentStep];

  const handleNext = () => {
    if (currentStep < tourSteps.length - 1) {
      const next = currentStep + 1;
      setCurrentStep(next);
      onSwitchTab(tourSteps[next].tabIndex);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      const prev = currentStep - 1;
      setCurrentStep(prev);
      onSwitchTab(tourSteps[prev].tabIndex);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>
          <X size={18} />
        </button>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'linear-gradient(135deg, #f59e0b, #d97706)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Award size={22} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#f59e0b', letterSpacing: '0.6px' }}>
              {step.category} • STEP {currentStep + 1} OF {tourSteps.length}
            </div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
              {step.title}
            </h3>
          </div>
        </div>

        {/* Content */}
        <div style={{ margin: '18px 0', fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.6' }}>
          <p>{step.description}</p>

          <div style={{ marginTop: '14px', background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', padding: '12px 14px', borderRadius: '8px', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <Sparkles size={16} color="#06B6D4" style={{ marginTop: '2px', flexShrink: 0 }} />
            <div style={{ fontSize: '0.84rem', color: '#67e8f9', fontWeight: 600 }}>
              {step.keyHighlight}
            </div>
          </div>
        </div>

        {/* Progress dots */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', margin: '20px 0' }}>
          {tourSteps.map((_, i) => (
            <div
              key={i}
              onClick={() => {
                setCurrentStep(i);
                onSwitchTab(tourSteps[i].tabIndex);
              }}
              style={{
                width: i === currentStep ? '24px' : '8px',
                height: '8px',
                borderRadius: '4px',
                background: i === currentStep ? '#06B6D4' : 'rgba(255, 255, 255, 0.2)',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            />
          ))}
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            className="btn-outline"
            onClick={handlePrev}
            disabled={currentStep === 0}
            style={{ opacity: currentStep === 0 ? 0.4 : 1 }}
          >
            <ChevronLeft size={16} />
            <span>Previous</span>
          </button>

          <button className="btn-primary" onClick={handleNext}>
            <span>{currentStep === tourSteps.length - 1 ? 'Start Exploring Prototype' : 'Next Step'}</span>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};
