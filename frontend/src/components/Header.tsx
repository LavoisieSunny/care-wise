import React from 'react';
import { Shield, AlertTriangle, Share2, Award, Zap, FileText } from 'lucide-react';
import { PolicyDetails } from '../types/policy';

interface HeaderProps {
  activePolicy: PolicyDetails | null;
  allPolicies: PolicyDetails[];
  onSelectPolicy: (policy: PolicyDetails) => void;
  emergencyMode: boolean;
  onToggleEmergency: () => void;
  onOpenSOS: () => void;
  onOpenDemoTour: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activePolicy,
  allPolicies,
  onSelectPolicy,
  emergencyMode,
  onToggleEmergency,
  onOpenSOS,
  onOpenDemoTour,
}) => {
  return (
    <header className="header-wrapper">
      <div className="container header-container">
        {/* Brand */}
        <div className="brand-section">
          <svg className="brand-logo-icon" viewBox="0 0 100 100" fill="none">
            <defs>
              <linearGradient id="hdrGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06B6D4" />
                <stop offset="100%" stopColor="#2563EB" />
              </linearGradient>
            </defs>
            <path d="M50 8 L85 22 C85 55 50 88 50 94 C50 88 15 55 15 22 Z" fill="#0F172A" stroke="url(#hdrGrad)" strokeWidth="5" />
            <rect x="44" y="32" width="12" height="32" rx="3" fill="#06B6D4" />
            <rect x="34" y="42" width="32" height="12" rx="3" fill="#06B6D4" />
            <circle cx="50" cy="48" r="3.5" fill="#FFFFFF" />
          </svg>
          <div>
            <div className="brand-title">CareWise</div>
            <div className="brand-tagline">Smart Decisions, Better Care</div>
          </div>
        </div>

        {/* Right actions */}
        <div className="header-actions">
          {/* Active Policy Selector */}
          <div className="policy-selector-pill" title="Click to switch active policy">
            <FileText size={15} color="#06B6D4" />
            <select
              style={{
                background: 'transparent',
                border: 'none',
                color: 'inherit',
                fontSize: '0.82rem',
                fontWeight: 600,
                outline: 'none',
                cursor: 'pointer',
                maxWidth: '200px',
              }}
              value={activePolicy?.id || ''}
              onChange={(e) => {
                const p = allPolicies.find((x) => x.id === e.target.value);
                if (p) onSelectPolicy(p);
              }}
            >
              {allPolicies.map((p) => (
                <option key={p.id} value={p.id} style={{ background: '#0F172A', color: '#fff' }}>
                  {p.insurer_name.split(' ')[0]} - ₹{(p.sum_insured / 100000).toFixed(0)}L
                </option>
              ))}
            </select>
          </div>

          {/* 2 AM Emergency Toggle */}
          <button
            className={`emergency-btn-toggle ${emergencyMode ? 'active' : ''}`}
            onClick={onToggleEmergency}
            title="Isolate nearest 100% cashless hospitals with available emergency beds"
          >
            <AlertTriangle size={15} />
            <span>{emergencyMode ? '🚨 2 AM Mode: Active' : '2 AM Emergency'}</span>
          </button>

          {/* SOS Share Button */}
          <button className="btn-sos" onClick={onOpenSOS} title="Generate family WhatsApp alert & checklist">
            <Share2 size={14} />
            <span>Family SOS</span>
          </button>

          {/* Demo Tour Button */}
          <button className="btn-judge-tour" onClick={onOpenDemoTour} title="Launch 90-sec Hackathon Judge Tour">
            <Award size={15} />
            <span>🏆 Judge Tour</span>
          </button>
        </div>
      </div>
    </header>
  );
};
