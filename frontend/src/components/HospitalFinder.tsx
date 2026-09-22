import React, { useState } from 'react';
import { 
  Building2, 
  MapPin, 
  PhoneCall, 
  Bed, 
  ShieldCheck, 
  ShieldX, 
  Navigation, 
  Zap, 
  Scale, 
  Filter 
} from 'lucide-react';
import { Hospital } from '../types/hospital';
import { PolicyDetails } from '../types/policy';

interface HospitalFinderProps {
  hospitals: Hospital[];
  activePolicy: PolicyDetails | null;
  emergencyMode: boolean;
  onSelectForCompare: (hospitalId: string) => void;
  selectedCompareIds: string[];
}

export const HospitalFinder: React.FC<HospitalFinderProps> = ({
  hospitals,
  activePolicy,
  emergencyMode,
  onSelectForCompare,
  selectedCompareIds,
}) => {
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('all');
  const [cashlessOnly, setCashlessOnly] = useState<boolean>(false);
  const [maxDistance, setMaxDistance] = useState<number>(20);

  const specialties = [
    { id: 'all', label: 'All Specialties' },
    { id: 'Cardiology', label: 'Cardiology / Heart' },
    { id: 'Emergency ICU', label: '24x7 Emergency ICU' },
    { id: 'Orthopedics', label: 'Orthopedics / Trauma' },
    { id: 'General Surgery', label: 'General Surgery' },
  ];

  const filteredHospitals = hospitals.filter((h) => {
    if (emergencyMode && (!h.emergency_24x7 || h.bed_availability.icu === 0)) return false;
    if (cashlessOnly && h.network_status !== 'CASHLESS_NETWORK') return false;
    if (h.distance_km > maxDistance) return false;
    if (selectedSpecialty !== 'all' && !h.specialties.includes(selectedSpecialty)) return false;
    return true;
  });

  return (
    <div>
      {/* 2 AM Emergency Mode Status Banner */}
      {emergencyMode && (
        <div className="glass-panel" style={{ background: 'linear-gradient(90deg, rgba(244, 63, 94, 0.15) 0%, rgba(136, 19, 55, 0.25) 100%)', border: '1px solid #f43f5e', padding: '16px 20px', marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#f43f5e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Zap size={20} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#ffe4e6' }}>
                🚨 2 AM EMERGENCY MODE ACTIVATED
              </div>
              <div style={{ fontSize: '0.82rem', color: '#fbcfe8' }}>
                Filtered strictly for hospitals with 24/7 emergency response, verified ICU beds, and 100% cashless TPA integration.
              </div>
            </div>
          </div>
          <div style={{ fontSize: '0.84rem', background: '#000', padding: '6px 14px', borderRadius: '20px', color: '#f43f5e', fontWeight: 700 }}>
            {filteredHospitals.length} Emergency Centres Ready
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} color="#06B6D4" />
          <span style={{ fontSize: '0.84rem', fontWeight: 600 }}>Filter by:</span>

          {/* Specialty */}
          <select
            className="filter-select"
            value={selectedSpecialty}
            onChange={(e) => setSelectedSpecialty(e.target.value)}
          >
            {specialties.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>

          {/* Max Distance */}
          <select
            className="filter-select"
            value={maxDistance}
            onChange={(e) => setMaxDistance(Number(e.target.value))}
          >
            <option value={5}>Within 5 km</option>
            <option value={10}>Within 10 km</option>
            <option value={20}>Within 20 km</option>
            <option value={50}>Within 50 km</option>
          </select>
        </div>

        <div className="filter-group">
          {/* Cashless Only Toggle */}
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.84rem' }}>
            <input
              type="checkbox"
              checked={cashlessOnly}
              onChange={(e) => setCashlessOnly(e.target.checked)}
              style={{ accentColor: '#06B6D4', width: 16, height: 16 }}
            />
            <span>100% Cashless Network Only</span>
          </label>
        </div>
      </div>

      {/* Hospital Cards Grid */}
      <div className="hospital-cards-grid">
        {filteredHospitals.map((h) => {
          const isSelected = selectedCompareIds.includes(h.id);
          const isCashless = h.network_status === 'CASHLESS_NETWORK';

          return (
            <div
              key={h.id}
              className={`hospital-card ${isCashless ? 'recommended-card' : 'risk-card'}`}
            >
              <div>
                <div className="hospital-header">
                  <div>
                    <h3 className="hospital-name">{h.name}</h3>
                    <div className="hospital-tagline">{h.tagline}</div>
                  </div>
                  <span className={`network-badge ${isCashless ? 'cashless' : 'non-network'}`}>
                    {isCashless ? 'CASHLESS' : 'REIMBURSEMENT ONLY'}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', margin: '10px 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={14} color="#06B6D4" />
                    <strong>{h.distance_km} km</strong> ({h.locality})
                  </span>
                  <span>•</span>
                  <span>Ambulance ETA: <strong style={{ color: '#38bdf8' }}>{h.estimated_ambulance_eta_mins} mins</strong></span>
                </div>

                {/* Bed availability live pill */}
                <div className="bed-status-pill">
                  <Bed size={15} />
                  <span>
                    <strong>{h.bed_availability.icu} ICU Beds</strong> • {h.bed_availability.single_private} Single AC
                  </span>
                </div>

                {/* Specialties tags */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', margin: '8px 0' }}>
                  {h.specialties.slice(0, 3).map((sp, i) => (
                    <span
                      key={i}
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.72rem',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        color: 'var(--text-muted)',
                      }}
                    >
                      {sp}
                    </span>
                  ))}
                </div>

                {/* Room tariffs quick indicator */}
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '8px 10px', borderRadius: '6px', margin: '8px 0', fontSize: '0.78rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Twin Sharing:</span>
                    <strong style={{ color: '#fff' }}>₹{h.room_tariffs.twin_sharing.toLocaleString('en-IN')}/day</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Single Private AC:</span>
                    <strong style={{ color: h.room_tariffs.single_private > (activePolicy?.room_limit.capped_amount_per_day || 5000) ? '#f59e0b' : '#34d399' }}>
                      ₹{h.room_tariffs.single_private.toLocaleString('en-IN')}/day
                    </strong>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="hospital-action-bar">
                <a
                  href={`tel:${h.emergency_contact}`}
                  className="btn-outline"
                  style={{ textDecoration: 'none' }}
                  title="Call 24/7 Emergency Desk"
                >
                  <PhoneCall size={14} color="#f43f5e" />
                  <span>{h.emergency_contact.slice(0, 14)}</span>
                </a>

                <button
                  className="btn-primary"
                  onClick={() => onSelectForCompare(h.id)}
                  style={{
                    background: isSelected ? 'var(--grad-emerald)' : undefined,
                  }}
                >
                  <Scale size={14} />
                  <span>{isSelected ? '✓ In Compare' : 'Compare Costs'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
