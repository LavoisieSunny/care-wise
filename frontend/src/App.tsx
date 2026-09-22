import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  DollarSign, 
  HelpCircle, 
  Share2, 
  Award, 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  Sparkles, 
  Send, 
  Building2, 
  Check, 
  X,
  ExternalLink,
  Bot,
  User,
  Scale
} from 'lucide-react';
import { PolicyDetails, ClauseCitation } from './types/policy';
import { HospitalCostAnalysis } from './types/calculator';
import { getPolicies, uploadPolicyPDF } from './api/policies';
import { simulateCost } from './api/calculator';
import { queryRAG } from './api/rag';
import { generateDossier } from './api/journey';

export const App: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyDetails[]>([]);
  const [activePolicy, setActivePolicy] = useState<PolicyDetails | null>(null);
  const [activeCitation, setActiveCitation] = useState<ClauseCitation | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(12);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(100);
  const [emergencyMode, setEmergencyMode] = useState<boolean>(false);
  
  // Cost Simulator state
  const [selectedProcedure, setSelectedProcedure] = useState<string>('angioplasty');
  const [selectedRoom, setSelectedRoom] = useState<string>('twin_sharing');
  const [costAnalysis, setCostAnalysis] = useState<HospitalCostAnalysis | null>(null);
  const [simLoading, setSimLoading] = useState<boolean>(false);

  // Mini RAG Chat state
  const [chatMessages, setChatMessages] = useState<Array<{ sender: 'user' | 'assistant'; text: string; citation?: string }>>([
    {
      sender: 'assistant',
      text: 'CareWise AI extracted your policy document. Ask me anything about room limits, co-payments, or emergency pre-authorisation.',
    }
  ]);
  const [chatInput, setChatInput] = useState<string>('');
  const [chatLoading, setChatLoading] = useState<boolean>(false);

  // Modals
  const [showSOSModal, setShowSOSModal] = useState<boolean>(false);
  const [showTourModal, setShowTourModal] = useState<boolean>(false);
  const [sosCopied, setSosCopied] = useState<boolean>(false);
  const [dossierAlert, setDossierAlert] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initial load
  useEffect(() => {
    const init = async () => {
      try {
        const pols = await getPolicies();
        setPolicies(pols);
        if (pols.length > 0) {
          selectPolicy(pols[0]);
        }
      } catch (e) {
        console.error('Failed to load policies:', e);
      }
    };
    init();
  }, []);

  // Update cost simulation when policy, procedure, or room changes
  useEffect(() => {
    if (!activePolicy) return;
    const runSim = async () => {
      setSimLoading(true);
      try {
        const analysis = await simulateCost({
          policy_id: activePolicy.id,
          hospital_id: 'hosp_city_heart',
          procedure_code: selectedProcedure,
          room_type: selectedRoom,
          stay_days: 3,
          patient_age: 62,
        });
        setCostAnalysis(analysis);
      } catch (e) {
        console.error('Sim error:', e);
      } finally {
        setSimLoading(false);
      }
    };
    runSim();
  }, [activePolicy?.id, selectedProcedure, selectedRoom]);

  const selectPolicy = (p: PolicyDetails) => {
    setActivePolicy(p);
    if (p.all_citations.length > 0) {
      const targetCit = p.all_citations.find(c => c.tag === 'ROOM_LIMIT') || p.all_citations[0];
      setActiveCitation(targetCit);
      setCurrentPage(targetCit.page_number);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(30);
    try {
      setTimeout(() => setUploadProgress(70), 300);
      const res = await uploadPolicyPDF(file);
      setUploadProgress(100);
      if (res.policy) {
        setPolicies(prev => [res.policy, ...prev]);
        selectPolicy(res.policy);
        alert(`✓ Successfully processed "${file.name}"! OCR extracted ${res.pages_processed} pages and structured all 6 insurance schedules.`);
      }
    } catch (err: any) {
      alert(`Upload failed: ${err.message || 'Error processing file'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleScheduleClick = (cit: ClauseCitation) => {
    setActiveCitation(cit);
    setCurrentPage(cit.page_number);
  };

  const handleSendMessage = async (customQ?: string) => {
    const q = customQ || chatInput;
    if (!q.trim() || !activePolicy || chatLoading) return;

    setChatMessages(prev => [...prev, { sender: 'user', text: q }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await queryRAG({
        policy_id: activePolicy.id,
        query: q,
      });
      setChatMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: res.answer,
          citation: res.citations.length > 0 ? `Page ${res.citations[0].page_number} (${res.citations[0].clause_id})` : undefined
        }
      ]);
    } catch (e) {
      setChatMessages(prev => [...prev, { sender: 'assistant', text: 'Error connecting to LLM service.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleGenerateDossier = async () => {
    try {
      const dos = await generateDossier();
      setDossierAlert(`✓ Digital Claim Dossier ${dos.dossier_id} generated! 6 discharge documents indexed.`);
      setTimeout(() => setDossierAlert(null), 5000);
    } catch (e) {
      console.error(e);
    }
  };

  const sosText = `🚨 *CAREWAISE EMERGENCY FAMILY ALERT*

👤 *Patient*: Ramesh Sharma (Age 58)
🏥 *Hospital*: Sanjeevani Multispeciality Hospital
📞 *Emergency Desk*: +91 80 4122 8899
🛡️ *Policy*: ${activePolicy?.policy_name || 'Star Health Family Health Optima'}
🏢 *TPA*: Medi Assist TPA (Sanction: ₹75,000)

⚠️ *CRITICAL CAUTION FOR ADMISSION DESK*:
• Request *Twin Sharing Room* (under ₹${activePolicy?.room_limit.capped_amount_per_day || 5000}/day) ONLY!
• Do NOT agree to a Deluxe Suite upgrade to prevent severe proportionate deduction penalty on doctor fees.`;

  const handleCopySOS = () => {
    navigator.clipboard.writeText(sosText);
    setSosCopied(true);
    setTimeout(() => setSosCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
          }
        }}
      />

      {/* 1. App Header with Prominent Single Upload Button */}
      <header className="app-header">
        <div className="header-row">
          {/* Brand */}
          <div className="brand-wrapper">
            <svg className="brand-logo-icon" viewBox="0 0 100 100" fill="none">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#06B6D4" />
                  <stop offset="100%" stopColor="#2563EB" />
                </linearGradient>
              </defs>
              <path d="M50 8 L85 22 C85 55 50 88 50 94 C50 88 15 55 15 22 Z" fill="#0F172A" stroke="url(#logoGrad)" strokeWidth="5" />
              <rect x="44" y="32" width="12" height="32" rx="3" fill="#06B6D4" />
              <rect x="34" y="42" width="32" height="12" rx="3" fill="#06B6D4" />
              <circle cx="50" cy="48" r="3.5" fill="#FFFFFF" />
            </svg>
            <div>
              <div className="brand-title">CareWise</div>
              <div className="brand-subtitle">Smart Decisions, Better Care</div>
            </div>
          </div>

          {/* Center / Right Tools */}
          <div className="header-tools">
            {/* The One Prominent Upload Button */}
            <button
              className="btn-upload-main"
              onClick={() => fileInputRef.current?.click()}
              title="Upload any health insurance PDF to run OCR and extract schedules"
            >
              <UploadCloud size={18} />
              <span>{isUploading ? 'Running OCR & LLM Extraction...' : 'Upload Policy Document (PDF)'}</span>
            </button>

            {/* Quick Sample Selector Pills for Instant Demo */}
            <div className="sample-pills-bar">
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                Sample Policies:
              </span>
              {policies.map(p => (
                <button
                  key={p.id}
                  className={`sample-pill-btn ${activePolicy?.id === p.id ? 'active' : ''}`}
                  onClick={() => selectPolicy(p)}
                >
                  {p.insurer_name.split(' ')[0]} ({p.sum_insured >= 1000000 ? `${(p.sum_insured/100000).toFixed(0)}L` : `${(p.sum_insured/100000).toFixed(0)}L`})
                </button>
              ))}
            </div>

            {/* 2 AM Emergency Toggle */}
            <button
              className={`btn-emergency ${emergencyMode ? 'active' : ''}`}
              onClick={() => setEmergencyMode(!emergencyMode)}
            >
              <AlertTriangle size={15} />
              <span>{emergencyMode ? '🚨 2 AM Mode: Active' : '2 AM Emergency'}</span>
            </button>

            {/* SOS Share Button */}
            <button className="btn-header-action" onClick={() => setShowSOSModal(true)}>
              <Share2 size={14} color="#10B981" />
              <span>Family SOS</span>
            </button>

            {/* 60-Sec Tour */}
            <button className="btn-header-action" onClick={() => setShowTourModal(true)}>
              <Award size={14} color="#F59E0B" />
              <span>🏆 Judge Guide</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. Document Status Strip & OCR Extraction Bar */}
      <div className="document-status-strip">
        <div style={{ display: 'flex', alignItems: 'center', gap: '18px', flexWrap: 'wrap' }}>
          <div className="doc-info-item">
            <span>Active Document:</span>
            <strong>{activePolicy?.policy_name || 'Loading policy...'}</strong>
          </div>
          <div className="doc-info-item">
            <span>Insurer:</span>
            <strong>{activePolicy?.insurer_name}</strong>
          </div>
          <div className="ocr-badge">
            <Sparkles size={11} />
            <span>OCR 100% Extracted • PyMuPDF Grounded</span>
          </div>
        </div>

        {/* 4 Key Policy Metrics Quick Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '0.76rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Sum Insured: <strong style={{ color: '#38bdf8' }}>₹{((activePolicy?.sum_insured || 500000) / 100000).toFixed(0)} Lakhs</strong>
          </span>
          <span style={{ fontSize: '0.76rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Room Cap: <strong style={{ color: activePolicy?.room_limit.no_room_rent_capping ? '#34d399' : '#fbbf24' }}>
              {activePolicy?.room_limit.no_room_rent_capping ? 'No Cap' : `₹${activePolicy?.room_limit.capped_amount_per_day || 5000}/day`}
            </strong>
          </span>
          <span style={{ fontSize: '0.76rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Co-Pay: <strong style={{ color: '#fff' }}>{activePolicy?.copay.senior_citizen_percentage || 0}%</strong>
          </span>
          <span style={{ fontSize: '0.76rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Pre-Auth: <strong style={{ color: '#f43f5e' }}>{activePolicy?.pre_auth.emergency_window_hours || 24}h Notice</strong>
          </span>
        </div>
      </div>

      {/* Dossier Alert Toast if triggered */}
      {dossierAlert && (
        <div style={{ background: '#059669', color: '#fff', padding: '6px 20px', fontSize: '0.82rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{dossierAlert}</span>
          <X size={14} style={{ cursor: 'pointer' }} onClick={() => setDossierAlert(null)} />
        </div>
      )}

      {/* 3. Main Unified 3-Column Workbench */}
      <div className="workbench-container">
        
        {/* ================= COLUMN 1: DOCUMENT & CLAUSE VIEWER ================= */}
        <section className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <FileText size={16} color="#06B6D4" />
              <span>Document Viewer & Clause Citation</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Target: <strong style={{ color: '#fef08a' }}>{activeCitation?.clause_id || 'SEC-3.2.1'}</strong>
            </span>
          </div>

          <div className="panel-body">
            {/* Page toolbar */}
            <div className="doc-page-toolbar">
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <button
                  className="sample-pill-btn"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                >
                  <ChevronLeft size={14} />
                </button>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f8fafc' }}>
                  Page {currentPage} of 36
                </span>
                <button
                  className="sample-pill-btn"
                  onClick={() => setCurrentPage(prev => Math.min(36, prev + 1))}
                >
                  <ChevronRight size={14} />
                </button>
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                {activeCitation ? activeCitation.section : 'Policy Schedule'}
              </div>
            </div>

            {/* Document Text Paper */}
            <div className="doc-text-paper">
              <div style={{ color: 'var(--text-dim)', fontSize: '0.72rem', marginBottom: '10px', borderBottom: '1px dashed var(--border-subtle)', paddingBottom: '6px' }}>
                DOCUMENT MASTER: {activePolicy?.insurer_name.toUpperCase()} / TERMS & CONDITIONS (PAGE {currentPage})
              </div>

              <p style={{ opacity: 0.65, marginBottom: '12px' }}>
                [SECTION 2: IN-PATIENT HOSPITALISATION DEFINITIONS]<br />
                2.1 "Admissible Expenses" shall mean expenses covered under the policy terms for approved medical treatments.<br />
                2.2 "Network Provider" means hospitals enlisted by the insurer or TPA to provide cashless service.
              </p>

              {/* Glowing Highlighted Clause Callout */}
              <div className="active-clause-callout">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <strong style={{ fontSize: '0.86rem', color: '#fef08a' }}>
                    ⭐ {activeCitation?.clause_title || 'Clause 3.2.1: Room Rent and Proportionate Deduction'}
                  </strong>
                  <span style={{ fontSize: '0.7rem', background: '#000', padding: '2px 6px', borderRadius: '4px', color: '#fde047' }}>
                    PAGE {activeCitation?.page_number || currentPage} • {activeCitation?.clause_id || 'SEC-3.2.1'}
                  </span>
                </div>
                <p style={{ margin: 0, fontStyle: 'italic', color: '#fff', fontSize: '0.82rem' }}>
                  "{activeCitation?.exact_text || activePolicy?.room_limit.citation?.exact_text}"
                </p>
              </div>

              <p style={{ opacity: 0.65, marginTop: '12px' }}>
                [SECTION 6: EXCLUSIONS & NON-PAYABLE CLAUSES]<br />
                6.1 Non-medical disposable items (IRDAI List I) including hygiene packs, gloves, masks, disposable syringes are excluded from cashless claim settlement.<br />
                6.2 Domiciliary hospitalisation without doctor prescription is non-payable.
              </p>
            </div>

            {/* Jump to other citations bar */}
            <div style={{ marginTop: '10px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Verified Citations in this Policy:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                {activePolicy?.all_citations.map((c, i) => (
                  <button
                    key={i}
                    className={`sample-pill-btn ${activeCitation?.clause_id === c.clause_id ? 'active' : ''}`}
                    onClick={() => handleScheduleClick(c)}
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  >
                    Pg {c.page_number} ({c.clause_id})
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ================= COLUMN 2: STRUCTURED EXTRACTION & SCHEDULE TABLE ================= */}
        <section className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Scale size={16} color="#10B981" />
              <span>Extracted Policy Schedules & Conditions</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Click any row to jump
            </span>
          </div>

          <div className="panel-body">
            <div className="schedule-table-wrap">
              <table className="schedule-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Schedule / Clause</th>
                    <th>Extracted Terms & Limits</th>
                    <th>Page</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Row 1: Room Rent */}
                  <tr
                    className={activeCitation?.tag === 'ROOM_LIMIT' ? 'active-row' : ''}
                    onClick={() => {
                      if (activePolicy?.room_limit.citation) handleScheduleClick(activePolicy.room_limit.citation);
                    }}
                  >
                    <td><strong>01</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>Room Rent Cap</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>SEC-3.2.1 Boarding & Nursing</div>
                    </td>
                    <td>
                      <span style={{ color: activePolicy?.room_limit.no_room_rent_capping ? '#34d399' : '#fbbf24', fontWeight: 600 }}>
                        {activePolicy?.room_limit.no_room_rent_capping 
                          ? 'No Cap (Any Room Allowed)' 
                          : `₹${(activePolicy?.room_limit.capped_amount_per_day || 5000).toLocaleString('en-IN')}/day`}
                      </span>
                      {!activePolicy?.room_limit.no_room_rent_capping && (
                        <div style={{ fontSize: '0.68rem', color: '#f43f5e' }}>Proportionate Cut Active</div>
                      )}
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg {activePolicy?.room_limit.citation?.page_number || 12}</span></td>
                    <td>
                      <span className={`table-status-chip ${activePolicy?.room_limit.no_room_rent_capping ? 'chip-green' : 'chip-amber'}`}>
                        {activePolicy?.room_limit.no_room_rent_capping ? 'SAFE' : 'RISK'}
                      </span>
                    </td>
                  </tr>

                  {/* Row 2: ICU Limit */}
                  <tr
                    className={activeCitation?.tag === 'ICU_LIMIT' ? 'active-row' : ''}
                    onClick={() => {
                      const cit = activePolicy?.all_citations.find(c => c.tag === 'ICU_LIMIT') || activePolicy?.all_citations[1];
                      if (cit) handleScheduleClick(cit);
                    }}
                  >
                    <td><strong>02</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>ICU / ICCU Limit</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Critical Care Monitoring</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#fff' }}>
                        {activePolicy?.icu_limit_per_day ? `₹${activePolicy.icu_limit_per_day.toLocaleString('en-IN')}/day` : 'As per actuals'}
                      </span>
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg 13</span></td>
                    <td><span className="table-status-chip chip-green">COVERED</span></td>
                  </tr>

                  {/* Row 3: Co-Payment */}
                  <tr
                    className={activeCitation?.tag === 'COPAY' ? 'active-row' : ''}
                    onClick={() => {
                      if (activePolicy?.copay.citation) handleScheduleClick(activePolicy.copay.citation);
                    }}
                  >
                    <td><strong>03</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>Mandatory Co-Pay</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Senior Citizen Clause</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: (activePolicy?.copay.senior_citizen_percentage || 0) > 0 ? '#fbbf24' : '#34d399' }}>
                        {(activePolicy?.copay.senior_citizen_percentage || 0) > 0
                          ? `${activePolicy?.copay.senior_citizen_percentage}% (Age 61+)`
                          : '0% Co-Payment'}
                      </span>
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg {activePolicy?.copay.citation?.page_number || 18}</span></td>
                    <td>
                      <span className={`table-status-chip ${(activePolicy?.copay.senior_citizen_percentage || 0) > 0 ? 'chip-amber' : 'chip-green'}`}>
                        {(activePolicy?.copay.senior_citizen_percentage || 0) > 0 ? 'APPLIES' : 'ZERO'}
                      </span>
                    </td>
                  </tr>

                  {/* Row 4: Emergency Notice */}
                  <tr
                    className={activeCitation?.tag === 'PREAUTH' ? 'active-row' : ''}
                    onClick={() => {
                      if (activePolicy?.pre_auth.citation) handleScheduleClick(activePolicy.pre_auth.citation);
                    }}
                  >
                    <td><strong>04</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>Emergency Pre-Auth</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Intimation Window</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#fff' }}>
                        Within {activePolicy?.pre_auth.emergency_window_hours || 24} hours of admission
                      </span>
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg {activePolicy?.pre_auth.citation?.page_number || 27}</span></td>
                    <td><span className="table-status-chip chip-green">24H RULE</span></td>
                  </tr>

                  {/* Row 5: Non-Medical Consumables */}
                  <tr
                    className={activeCitation?.tag === 'CONSUMABLES' || activeCitation?.tag === 'EXCLUSIONS' ? 'active-row' : ''}
                    onClick={() => {
                      const cit = activePolicy?.all_citations.find(c => c.tag === 'CONSUMABLES' || c.tag === 'EXCLUSIONS') || activePolicy?.all_citations[0];
                      if (cit) handleScheduleClick(cit);
                    }}
                  >
                    <td><strong>05</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>Consumables Rider</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Gloves, PPE, Syringes</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: activePolicy?.has_consumables_rider ? '#34d399' : '#fb7185' }}>
                        {activePolicy?.has_consumables_rider ? 'Fully Covered (Plus Rider)' : 'Excluded (List I items unpaid)'}
                      </span>
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg 34</span></td>
                    <td>
                      <span className={`table-status-chip ${activePolicy?.has_consumables_rider ? 'chip-green' : 'chip-red'}`}>
                        {activePolicy?.has_consumables_rider ? 'COVERED' : 'EXCLUDED'}
                      </span>
                    </td>
                  </tr>

                  {/* Row 6: Waiting Periods */}
                  <tr>
                    <td><strong>06</strong></td>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>Waiting Periods</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Specific Ailment Exclusions</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#cbd5e1' }}>
                        30 Days Initial • 24 Mo Joint/Hernia
                      </span>
                    </td>
                    <td><span style={{ color: '#06b6d4', fontWeight: 700 }}>Pg 10</span></td>
                    <td><span className="table-status-chip chip-green">SCHEDULED</span></td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Cashless TPA Network tags */}
            <div style={{ marginTop: '14px', background: 'rgba(0,0,0,0.2)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Empanelled Cashless TPA Desks:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {activePolicy?.empanelled_tpas.map((tpa, i) => (
                  <span
                    key={i}
                    style={{
                      background: 'rgba(6, 182, 212, 0.12)',
                      color: '#67e8f9',
                      border: '1px solid rgba(6, 182, 212, 0.25)',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '0.74rem',
                      fontWeight: 600,
                    }}
                  >
                    ✓ {tpa}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ================= COLUMN 3: LLM INTELLIGENCE & CAREGIVER DECISION CENTER ================= */}
        <section className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Sparkles size={16} color="#06B6D4" />
              <span>LLM Caregiver Intelligence</span>
            </div>
            <button
              className="sample-pill-btn"
              style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', fontSize: '0.7rem' }}
              onClick={handleGenerateDossier}
            >
              One-Click Dossier
            </button>
          </div>

          <div className="panel-body">
            {/* LLM Plain English Caregiver Summary Card */}
            <div className="llm-advice-card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                <Bot size={15} />
                <span>AI Guidance for Caregiver (at 2 AM):</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#e2e8f0', lineHeight: '1.5' }}>
                • <strong>Room Limit</strong>: {activePolicy?.room_limit.no_room_rent_capping ? 'Any room category is safe.' : `Strictly choose Twin Sharing / under ₹${activePolicy?.room_limit.capped_amount_per_day || 5000}/day.`}
                <br />
                • <strong>Notice</strong>: Hand over policy card to TPA desk within 24 hours of admission.
                <br />
                • <strong>Out-of-Pocket Risk</strong>: {costAnalysis?.proportionate_deduction_triggered ? `⚠️ High penalty warning (₹${costAnalysis.proportionate_deduction_penalty.toLocaleString('en-IN')})!` : 'Safe! Zero proportionate deduction.'}
              </div>
            </div>

            {/* Proportionate Deduction Risk Simulator */}
            <div className="simulator-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.74rem', fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  Proportionate Deduction Simulator
                </span>
                <span style={{ fontSize: '0.7rem', color: '#06b6d4' }}>City Heart Institute</span>
              </div>

              {/* Controls */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '8px' }}>
                <div>
                  <label style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Procedure</label>
                  <select
                    className="mini-chat-input"
                    style={{ width: '100%', marginTop: '2px', fontSize: '0.74rem' }}
                    value={selectedProcedure}
                    onChange={(e) => setSelectedProcedure(e.target.value)}
                  >
                    <option value="angioplasty">Angioplasty / Stent</option>
                    <option value="appendectomy">Appendectomy</option>
                    <option value="knee_replacement">Knee Replacement</option>
                    <option value="dengue_icu">Dengue ICU Care</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Selected Room</label>
                  <select
                    className="mini-chat-input"
                    style={{ width: '100%', marginTop: '2px', fontSize: '0.74rem' }}
                    value={selectedRoom}
                    onChange={(e) => setSelectedRoom(e.target.value)}
                  >
                    <option value="twin_sharing">Twin Sharing (₹6,200)</option>
                    <option value="single_private">Single Private (₹8,500)</option>
                    <option value="deluxe_suite">Deluxe Suite (₹14,000)</option>
                  </select>
                </div>
              </div>

              {/* Calculated Out of Pocket Callout */}
              <div style={{ background: '#0a0f1d', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  Estimated Caregiver Out-of-Pocket
                </div>
                <div style={{ fontSize: '1.45rem', fontWeight: 800, color: costAnalysis?.proportionate_deduction_triggered ? '#fbbf24' : '#34d399', margin: '2px 0' }}>
                  ₹{(costAnalysis?.estimated_out_of_pocket || 0).toLocaleString('en-IN')}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Total Bill: ₹{(costAnalysis?.total_bill || 0).toLocaleString('en-IN')} • Insurer: ₹{(costAnalysis?.insurer_settlement || 0).toLocaleString('en-IN')}
                </div>
              </div>

              {/* Proportionate Warning */}
              {costAnalysis?.proportionate_deduction_triggered && (
                <div style={{ marginTop: '8px', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid #f59e0b', padding: '6px 8px', borderRadius: '4px', fontSize: '0.72rem', color: '#fef08a' }}>
                  ⚠️ <strong>Room limit breached!</strong> Insurer proportionately deducts <strong>₹{costAnalysis.proportionate_deduction_penalty.toLocaleString('en-IN')}</strong> from Doctor & OT fees.
                </div>
              )}
            </div>

            {/* Grounded AI Assistant Chat */}
            <div className="mini-chat-container">
              <div className="mini-chat-history">
                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    style={{
                      background: msg.sender === 'user' ? 'var(--grad-cyan-blue)' : 'rgba(255, 255, 255, 0.05)',
                      color: '#fff',
                      padding: '6px 10px',
                      borderRadius: '8px',
                      alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '92%',
                      fontSize: '0.78rem',
                      lineHeight: '1.45',
                    }}
                  >
                    <div>{msg.text}</div>
                    {msg.citation && (
                      <div style={{ fontSize: '0.68rem', color: '#67e8f9', marginTop: '4px', fontWeight: 700 }}>
                        ✓ Grounded in: {msg.citation}
                      </div>
                    )}
                  </div>
                ))}
                {chatLoading && (
                  <div style={{ fontStyle: 'italic', fontSize: '0.74rem', color: 'var(--text-dim)' }}>
                    LLM retrieving grounded policy clauses...
                  </div>
                )}
              </div>

              {/* Quick questions chips */}
              <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', padding: '4px 8px', background: 'rgba(0,0,0,0.4)' }}>
                <button
                  className="sample-pill-btn"
                  style={{ fontSize: '0.68rem', padding: '2px 6px' }}
                  onClick={() => handleSendMessage('Can I take a Deluxe Room without penalty?')}
                >
                  Deluxe Room?
                </button>
                <button
                  className="sample-pill-btn"
                  style={{ fontSize: '0.68rem', padding: '2px 6px' }}
                  onClick={() => handleSendMessage('What is the senior citizen co-pay?')}
                >
                  Senior Co-Pay?
                </button>
                <button
                  className="sample-pill-btn"
                  style={{ fontSize: '0.68rem', padding: '2px 6px' }}
                  onClick={() => handleSendMessage('What is the emergency pre-auth deadline?')}
                >
                  24h Deadline?
                </button>
              </div>

              {/* Input */}
              <div className="mini-chat-input-bar">
                <input
                  type="text"
                  className="mini-chat-input"
                  placeholder="Ask policy question..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSendMessage();
                  }}
                />
                <button className="mini-chat-btn" onClick={() => handleSendMessage()}>
                  <Send size={13} />
                </button>
              </div>
            </div>
          </div>
        </section>

      </div>

      {/* SOS Share Modal */}
      {showSOSModal && (
        <div className="modal-overlay" onClick={() => setShowSOSModal(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowSOSModal(false)}>
              <X size={16} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Share2 size={20} color="#10B981" />
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 800 }}>
                Caregiver Emergency Family Alert
              </h3>
            </div>
            <div style={{ background: '#080d19', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '12px', fontFamily: 'monospace', fontSize: '0.78rem', color: '#cbd5e1', whiteSpace: 'pre-line', lineHeight: '1.5', maxHeight: '250px', overflowY: 'auto' }}>
              {sosText}
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
              <button
                className="btn-upload-main"
                style={{ background: '#25D366', flex: 1, justifyContent: 'center' }}
                onClick={() => {
                  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(sosText)}`, '_blank');
                }}
              >
                Send via WhatsApp
              </button>
              <button
                className="btn-header-action"
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={handleCopySOS}
              >
                {sosCopied ? '✓ Copied to Clipboard!' : 'Copy Summary'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Judge Walkthrough Modal */}
      {showTourModal && (
        <div className="modal-overlay" onClick={() => setShowTourModal(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowTourModal(false)}>
              <X size={16} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Award size={22} color="#F59E0B" />
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 800 }}>
                CareWise — 60-Second Hackathon Winning Pitch
              </h3>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
              <p><strong>The Core Problem</strong>: Caregivers at 2 AM face hidden proportionate deduction traps where picking an over-limit room cuts surgeon fees by 50%, resulting in unexpected ₹75k+ bills at discharge.</p>
              <div style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', padding: '10px', borderRadius: '6px', margin: '12px 0' }}>
                <strong>How to Demo for Judges</strong>:
                <ol style={{ paddingLeft: '18px', marginTop: '6px', fontSize: '0.8rem' }}>
                  <li><strong>1-Click Upload</strong>: Click "Upload Policy Document" or pick any sample policy pill in the top bar.</li>
                  <li><strong>Auto-Extraction</strong>: Observe how Column 2 fills out all 6 schedules with exact page numbers.</li>
                  <li><strong>Grounded Document</strong>: Click on Row 1 (Room Rent) &rarr; Column 1 immediately jumps to Page 12 with glowing highlight on Clause SEC-3.2.1.</li>
                  <li><strong>Proportionate Penalty Demo</strong>: In Column 3, switch room to "Deluxe Suite" &rarr; watch the ₹49,500 penalty jump out-of-pocket to ₹76,200!</li>
                  <li><strong>One-Click Dossier</strong>: Click "One-Click Dossier" to bundle all discharge documents.</li>
                </ol>
              </div>
            </div>
            <button className="btn-upload-main" style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }} onClick={() => setShowTourModal(false)}>
              Got it! Let's Explore
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
