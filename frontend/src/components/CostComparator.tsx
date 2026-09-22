import React, { useState, useEffect } from 'react';
import { 
  Scale, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  HelpCircle, 
  DollarSign, 
  ArrowRight,
  Sparkles,
  Info
} from 'lucide-react';
import { HospitalCostAnalysis, CompareHospitalsResponse } from '../types/calculator';
import { PolicyDetails } from '../types/policy';
import { compareHospitals } from '../api/calculator';

interface CostComparatorProps {
  policy: PolicyDetails;
  selectedHospitalIds: string[];
}

export const CostComparator: React.FC<CostComparatorProps> = ({
  policy,
  selectedHospitalIds,
}) => {
  const [procedureCode, setProcedureCode] = useState<string>('angioplasty');
  const [roomType, setRoomType] = useState<string>('twin_sharing');
  const [stayDays, setStayDays] = useState<number>(3);
  const [patientAge, setPatientAge] = useState<number>(55);
  const [comparisonData, setComparisonData] = useState<CompareHospitalsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Default hospital IDs to compare if none selected
  const activeHospitalIds = selectedHospitalIds.length >= 2 
    ? selectedHospitalIds.slice(0, 3) 
    : ['hosp_sanjeevani', 'hosp_city_heart', 'hosp_carewell'];

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const data = await compareHospitals({
        policy_id: policy.id,
        hospital_ids: activeHospitalIds,
        procedure_code: procedureCode,
        room_type: roomType,
        stay_days: stayDays,
        patient_age: patientAge,
      });
      setComparisonData(data);
    } catch (err) {
      console.error('Failed to calculate comparison:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison();
  }, [policy.id, procedureCode, roomType, stayDays, patientAge, selectedHospitalIds.join(',')]);

  const procedures = [
    { id: 'angioplasty', label: 'Coronary Angioplasty (PTCA Stent)', defaultDays: 3 },
    { id: 'appendectomy', label: 'Laparoscopic Appendectomy', defaultDays: 2 },
    { id: 'knee_replacement', label: 'Total Knee Replacement', defaultDays: 4 },
    { id: 'dengue_icu', label: 'Severe Dengue ICU Care', defaultDays: 5 },
  ];

  const roomOptions = [
    { id: 'twin_sharing', label: 'Twin Sharing Room' },
    { id: 'single_private', label: 'Single Private AC Room' },
    { id: 'deluxe_suite', label: 'Deluxe / Executive Suite' },
  ];

  return (
    <div>
      {/* Comparator Controls */}
      <div className="comparison-controls-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
              Side-by-Side Cost & Financial Risk Simulator
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Simulates real-world hospital bills against your policy's room rent limit to expose hidden proportionate deduction penalties.
            </p>
          </div>

          {comparisonData && comparisonData.savings_vs_riskiest > 0 && (
            <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '6px 14px', borderRadius: '30px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={14} color="#10B981" />
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#16a34a' }}>
                CareWise protects you from up to ₹{comparisonData.savings_vs_riskiest.toLocaleString('en-IN')} in surprise bills!
              </span>
            </div>
          )}
        </div>

        {/* Inputs Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
          {/* Procedure */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
              Procedure / Treatment
            </label>
            <select
              className="filter-select"
              style={{ width: '100%', marginTop: '6px' }}
              value={procedureCode}
              onChange={(e) => {
                setProcedureCode(e.target.value);
                const p = procedures.find((x) => x.id === e.target.value);
                if (p) setStayDays(p.defaultDays);
              }}
            >
              {procedures.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Room Category */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
              Selected Room Category
            </label>
            <select
              className="filter-select"
              style={{ width: '100%', marginTop: '6px' }}
              value={roomType}
              onChange={(e) => setRoomType(e.target.value)}
            >
              {roomOptions.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {/* Patient Age */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
              Patient Age ({patientAge} years)
            </label>
            <input
              type="range"
              min="20"
              max="80"
              value={patientAge}
              onChange={(e) => setPatientAge(Number(e.target.value))}
              style={{ width: '100%', marginTop: '14px', accentColor: '#0b3a72' }}
            />
          </div>

          {/* Stay Duration */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
              Estimated Inpatient Stay
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                min="1"
                max="30"
                value={stayDays}
                onChange={(e) => setStayDays(Number(e.target.value))}
                className="filter-select"
                style={{ width: '70px', textAlign: 'center' }}
              />
              <span style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>Days Inpatient</span>
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Cards Grid */}
      {loading ? (
        <div className="glass-panel" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Computing proportionate deductions and out-of-pocket liabilities...
        </div>
      ) : (
        <div className="comparison-grid">
          {comparisonData?.comparisons.map((c) => {
            const isRec = c.risk_tier === 'RECOMMENDED';
            const isRisk = c.risk_tier === 'FINANCIAL_RISK';
            const isNonNet = c.risk_tier === 'NOT_ELIGIBLE';

            return (
              <div
                key={c.hospital_id}
                className={`compare-card ${isRec ? 'recommended' : isRisk ? 'financial-risk' : 'not-eligible'}`}
              >
                {/* Risk Tier Badge */}
                <div>
                  <span
                    className={`risk-badge-large ${isRec ? 'recommended' : isRisk ? 'financial-risk' : 'not-eligible'}`}
                  >
                    {isRec && <CheckCircle size={15} />}
                    {isRisk && <AlertTriangle size={15} />}
                    {isNonNet && <XCircle size={15} />}
                    <span>{isRec ? 'RECOMMENDED' : isRisk ? 'FINANCIAL RISK' : 'NOT ELIGIBLE'}</span>
                  </span>

                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, marginBottom: '2px' }}>
                    {c.hospital_name}
                  </h3>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Room: <strong>{c.room_type_label}</strong> (₹{c.daily_room_charge.toLocaleString('en-IN')}/day)
                  </div>
                </div>

                {/* Big Out of Pocket Callout */}
                <div className="oop-callout-box">
                  <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-dim)', fontWeight: 700 }}>
                    Estimated Caregiver Out-of-Pocket
                  </div>
                  <div className={`oop-amount ${isRec ? 'green' : isRisk ? 'amber' : 'red'}`}>
                    ₹{c.estimated_out_of_pocket.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {isNonNet 
                      ? 'No cashless. 100% upfront payment required.'
                      : `Insurer covers: ₹${c.insurer_settlement.toLocaleString('en-IN')}`}
                  </div>
                </div>

                {/* Proportionate Deduction Warning Box */}
                {c.proportionate_deduction_triggered && (
                  <div className="prop-deduction-alert">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, color: '#f59e0b', marginBottom: '4px' }}>
                      <AlertTriangle size={15} />
                      <span>PROPORTIONATE DEDUCTION APPLIED!</span>
                    </div>
                    <div>
                      Hospital charges <strong>₹{c.daily_room_charge.toLocaleString('en-IN')}/day</strong> vs your policy limit of <strong>₹{c.policy_room_limit_daily.toLocaleString('en-IN')}/day</strong>.
                      The insurer penalizes you with a <strong>₹{c.proportionate_deduction_penalty.toLocaleString('en-IN')}</strong> reduction across doctor and OT charges!
                    </div>
                  </div>
                )}

                {/* Breakdown List */}
                <div style={{ marginTop: '12px', flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Transparent Bill Breakdown:
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {c.breakdown.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'rgba(255, 255, 255, 0.02)',
                          padding: '8px 10px',
                          borderRadius: '6px',
                          fontSize: '0.8rem',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                          <span>{item.category}</span>
                          <span style={{ color: item.caregiver_out_of_pocket > 0 ? '#f59e0b' : '#16a34a' }}>
                            {item.caregiver_out_of_pocket > 0
                              ? `+ ₹${item.caregiver_out_of_pocket.toLocaleString('en-IN')} OOP`
                              : '₹0 OOP'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                          {item.notes}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action button */}
                <div style={{ marginTop: '20px' }}>
                  <button
                    className="btn-primary"
                    style={{
                      width: '100%',
                      background: isRec ? 'var(--grad-emerald)' : isRisk ? 'var(--grad-warning)' : 'var(--grad-danger)',
                    }}
                    onClick={() => alert(`Selected ${c.hospital_name} for admission. Advance to Journey Tracker to follow pre-authorization.`)}
                  >
                    <span>{isRec ? 'Select Safe Cashless Hospital' : 'Proceed with Caution'}</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
