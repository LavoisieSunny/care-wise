import React, { useState } from 'react';
import { Menu, X, FileText, AlertTriangle, Share2, Award, LayoutGrid, Activity, LogOut } from 'lucide-react';

interface SidebarProps {
  viewMode: 'studio' | 'journey';
  setViewMode: (m: 'studio' | 'journey') => void;
  policies: any[];
  activePolicy: any;
  selectPolicy: (p: any) => void;
  emergencyMode: boolean;
  onToggleEmergency: () => void;
  onOpenSOS: () => void;
  onOpenDemoTour: () => void;
  onLogout?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = (props) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button className="hamburger-btn" onClick={() => setOpen(!open)} aria-label="Toggle navigation menu">
        {open ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside className={`app-sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <FileText size={22} color="#0b3a72" />
          <div><div className="brand-title">CareWise</div><div className="brand-tagline">Smart Decisions, Better Care</div></div>
        </div>

        <nav className="sidebar-nav">
          <button className={`nav-item ${props.viewMode === 'studio' ? 'active' : ''}`} onClick={() => props.setViewMode('studio')}>
            <LayoutGrid size={16} /><span>Policy Grounding Studio</span>
          </button>
          <button className={`nav-item ${props.viewMode === 'journey' ? 'active' : ''}`} onClick={() => props.setViewMode('journey')}>
            <Activity size={16} /><span>Inpatient Journey Tracker</span>
          </button>
          <div className="nav-divider" />
          <button className={`nav-item ${props.emergencyMode ? 'active' : ''}`} onClick={props.onToggleEmergency}>
            <AlertTriangle size={16} /><span>2 AM Emergency</span>
          </button>
          <button className="nav-item" onClick={props.onOpenSOS}><Share2 size={16} /><span>Family SOS</span></button>
          <button className="nav-item" onClick={props.onOpenDemoTour}><Award size={16} /><span>Judge Tour</span></button>
          {props.onLogout && (
            <button className="nav-item" onClick={props.onLogout} style={{ marginTop: '8px', color: '#dc2626' }}>
              <LogOut size={16} /><span>Log Out</span>
            </button>
          )}
        </nav>

        <div className="sidebar-divider-label">Sample Policies</div>
        <div className="sidebar-policy-list">
          {props.policies.map((p) => (
            <button
              key={p.id}
              className={`sidebar-policy-item ${props.activePolicy?.id === p.id ? 'active' : ''}`}
              onClick={() => props.selectPolicy(p)}
            >
              {p.insurer_name.split(' ')[0]} ({((p.sum_insured || 500000) / 100000).toFixed(0)}L)
            </button>
          ))}
        </div>
      </aside>

      {open && <div className="sidebar-overlay" onClick={() => setOpen(false)} />}
    </>
  );
};
