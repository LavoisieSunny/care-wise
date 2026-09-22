import React, { useState } from 'react';
import { X, Copy, Check, MessageSquare, ShieldAlert, Phone } from 'lucide-react';
import { PolicyDetails } from '../types/policy';

interface SOSShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  policy: PolicyDetails | null;
}

export const SOSShareModal: React.FC<SOSShareModalProps> = ({
  isOpen,
  onClose,
  policy,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const roomCapText = policy?.room_limit.no_room_rent_capping
    ? 'Any Room Category (No Capping)'
    : `₹${(policy?.room_limit.capped_amount_per_day || 5000).toLocaleString('en-IN')}/day (${policy?.room_limit.allowed_room_category || 'Twin Sharing'})`;

  const shareText = `🚨 *CAREWAISE EMERGENCY FAMILY ALERT*

👤 *Patient*: Ramesh Sharma (Age 58)
🏥 *Hospital*: Sanjeevani Multispeciality Hospital
📞 *Emergency Desk*: +91 80 4122 8899
🛡️ *Insurance Policy*: ${policy?.policy_name || 'Star Health Family Health Optima'}
🏢 *TPA*: Medi Assist TPA (Pre-auth Ref: MA-992182)
✅ *Status*: Initial Cashless Approval Granted (₹75,000)

⚠️ *CRITICAL INSTRUCTION FOR FAMILY ARRIVING AT ADMISSION DESK*:
• Request *${roomCapText}* ONLY.
• Do NOT agree to a Deluxe Room upgrade to avoid a 50% proportionate deduction penalty on doctor & OT fees!
• Hand over patient Aadhaar card at TPA counter.

Track live updates: https://carewise.health/track/ADM-2026-89410`;

  const handleCopy = () => {
    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleWhatsApp = () => {
    const encoded = encodeURIComponent(shareText);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, '_blank');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>
          <X size={18} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShieldAlert size={20} color="#10B981" />
          </div>
          <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.3rem', fontWeight: 800 }}>
              Caregiver Emergency SOS Family Broadcast
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Broadcast instant hospital coordinates, TPA details, and room cap warnings to family members.
            </p>
          </div>
        </div>

        {/* Message Preview Box */}
        <div style={{ background: '#f1f5f9', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px', fontFamily: 'monospace', fontSize: '0.84rem', color: '#334155', whiteSpace: 'pre-line', lineHeight: '1.6', maxHeight: '280px', overflowY: 'auto' }}>
          {shareText}
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
          <button className="btn-primary" style={{ background: '#25D366' }} onClick={handleWhatsApp}>
            <MessageSquare size={16} />
            <span>Send via WhatsApp</span>
          </button>

          <button className="btn-outline" style={{ flex: 1 }} onClick={handleCopy}>
            {copied ? <Check size={16} color="#10B981" /> : <Copy size={16} />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Summary'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
