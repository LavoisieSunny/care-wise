import React, { useState } from 'react';
import { X, Search, Globe, ExternalLink, Sparkles } from 'lucide-react';
import { getMarketInsight, MarketInsightResult } from '../api/market';

interface MarketInsightModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SUGGESTED_QUERIES = [
  'Best family floater plans for parents above 60',
  'How does room rent capping typically work across insurers',
  'What do most insurers cover for maternity waiting periods',
];

export const MarketInsightModal: React.FC<MarketInsightModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MarketInsightResult | null>(null);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const runSearch = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await getMarketInsight(q);
      setResult(res);
    } catch (err) {
      setError('Could not fetch market insight right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="caregiver-drawer-overlay" onClick={onClose} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-panel" onClick={(e) => e.stopPropagation()} style={{ width: '560px', maxWidth: '92vw', maxHeight: '82vh', display: 'flex', flexDirection: 'column', background: '#fff' }}>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Globe size={18} color="var(--color-primary)" />
            <span style={{ fontWeight: 800, fontSize: '0.98rem', color: 'var(--text-main)' }}>Market Insights</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={20} color="#64748b" />
          </button>
        </div>

        <div style={{ padding: '16px 20px', overflowY: 'auto', flex: 1 }}>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
            Ask about general market trends across insurers — this searches the live web and cites its sources.
            It's general information, not personalized advice. Always confirm details directly with the insurer.
          </p>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
            <input
              className="chat-input"
              placeholder="e.g. Best floater plans for senior parents"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && runSearch(query)}
              style={{ flex: 1 }}
            />
            <button className="chat-send-btn" onClick={() => runSearch(query)} disabled={loading}>
              <Search size={16} />
            </button>
          </div>

          <div className="quick-prompts" style={{ padding: 0, marginBottom: '14px' }}>
            {SUGGESTED_QUERIES.map((q) => (
              <button key={q} className="prompt-chip" onClick={() => { setQuery(q); runSearch(q); }}>
                {q}
              </button>
            ))}
          </div>

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.84rem', padding: '20px 0' }}>
              <Sparkles size={16} className="spin" /> Searching the web for current market info...
            </div>
          )}

          {error && <div style={{ color: '#dc2626', fontSize: '0.82rem' }}>{error}</div>}

          {result && (
            <div className="chat-bubble assistant" style={{ maxWidth: '100%' }}>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', lineHeight: 1.6 }}>{result.answer}</div>

              {result.sources.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Sources
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {result.sources.map((s, i) => (
                      <a
                        key={i}
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="chat-citation-tag"
                        style={{ textDecoration: 'none' }}
                      >
                        <ExternalLink size={11} />
                        <span>{s.title || s.url}</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
