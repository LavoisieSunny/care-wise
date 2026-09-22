import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, ChevronRight, Globe } from 'lucide-react';
import { PolicyDetails, ClauseCitation } from '../types/policy';
import { ChatMessage } from '../types/rag';
import { queryRAG } from '../api/rag';

interface GroundedRAGChatProps {
  policy: PolicyDetails;
  onCitationClick: (citation: ClauseCitation) => void;
}

export const GroundedRAGChat: React.FC<GroundedRAGChatProps> = ({
  policy,
  onCitationClick,
}) => {
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: `Hello! I am your CareWise Grounded Policy Assistant for **${policy.policy_name}**. Ask me any question about room categories, co-payments, emergency pre-authorisation, or exclusions. All answers are grounded with exact document citations.`,
      timestamp: 'Just now',
      suggested_actions: [
        'Check room rent capping rules',
        'Senior citizen co-pay terms',
        '2 AM emergency intimation window',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const quickPromptsEn = [
    'Can I pick a Single Deluxe Room without losing money?',
    'What is the senior citizen co-pay percentage?',
    'What is the emergency pre-auth deadline?',
    'Are surgical consumables and gloves covered?',
  ];

  const quickPromptsHi = [
    'क्या मैं बिना पेनल्टी के डीलक्स रूम ले सकता हूँ?',
    'सीनियर सिटीजन को-पे प्रतिशत कितना है?',
    'इमरजेंसी प्री-ऑथ की समय सीमा क्या है?',
    'क्या सर्जिकल सामग्री और ग्लव्स कवर हैं?',
  ];

  const quickPrompts = language === 'hi' ? quickPromptsHi : quickPromptsEn;

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await queryRAG({
        policy_id: policy.id,
        query: q,
        language: language,
      });

      const assistantMsg: ChatMessage = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: res.citations,
        suggested_actions: res.suggested_actions,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `asst-err-${Date.now()}`,
          sender: 'assistant',
          text: language === 'hi'
            ? 'RAG सेवा से कनेक्ट करने में असमर्थ। कृपया सुनिश्चित करें कि बैकएंड चल रहा है।'
            : 'Unable to reach RAG service. Please ensure the backend is running.',
          timestamp: 'Now',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-chat-panel">
      {/* Header */}
      <div className="rag-chat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--grad-cyan-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bot size={16} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>Caregiver Policy Assistant</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>Zero Hallucination • Grounded with Citations</div>
          </div>
        </div>

        {/* Hindi/English Accessibility Language Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255, 255, 255, 0.04)', padding: '2px 4px', borderRadius: '14px', border: '1px solid var(--border-subtle)' }}>
          <Globe size={13} color="#38BDF8" style={{ marginLeft: 3 }} />
          <button
            type="button"
            onClick={() => setLanguage('en')}
            style={{
              background: language === 'en' ? 'var(--grad-cyan-blue)' : 'transparent',
              color: language === 'en' ? '#fff' : 'var(--text-dim)',
              border: 'none',
              borderRadius: '10px',
              padding: '2px 8px',
              fontSize: '0.72rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            EN
          </button>
          <button
            type="button"
            onClick={() => setLanguage('hi')}
            style={{
              background: language === 'hi' ? 'var(--grad-cyan-blue)' : 'transparent',
              color: language === 'hi' ? '#fff' : 'var(--text-dim)',
              border: 'none',
              borderRadius: '10px',
              padding: '2px 8px',
              fontSize: '0.72rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            हिंदी
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages-container">
        {messages.map((m) => (
          <div key={m.id} className={`chat-bubble ${m.sender}`}>
            <div style={{ fontSize: '0.75rem', opacity: 0.6, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              {m.sender === 'assistant' ? <Bot size={12} /> : <User size={12} />}
              <span>{m.sender === 'assistant' ? 'CareWise AI' : 'You'}</span> • {m.timestamp}
            </div>

            <div style={{ whiteSpace: 'pre-line' }}>{m.text}</div>

            {/* Citations Badges */}
            {m.citations && m.citations.length > 0 && (
              <div style={{ marginTop: '10px' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <BookOpen size={12} color="#06B6D4" />
                  <span>
                    {language === 'hi' ? 'सत्यापित उद्धरण (दस्तावेज़ में देखने के लिए क्लिक करें):' : 'VERIFIED CITATIONS (Click to view in document):'}
                  </span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {m.citations.map((c, i) => (
                    <div
                      key={i}
                      className="chat-citation-tag"
                      onClick={() => onCitationClick(c)}
                      title="Click to jump to highlighted page"
                    >
                      <Sparkles size={11} />
                      <strong>{language === 'hi' ? `पृष्ठ ${c.page_number}` : `Page ${c.page_number}`}</strong> • {c.clause_id}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Suggested Caregiver Actions */}
            {m.suggested_actions && m.suggested_actions.length > 0 && (
              <div style={{ marginTop: '10px', background: 'rgba(0,0,0,0.25)', padding: '8px 10px', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.72rem', color: '#67e8f9', fontWeight: 700, marginBottom: '4px' }}>
                  {language === 'hi' ? 'अनुशंसित अगले कदम:' : 'RECOMMENDED NEXT ACTIONS:'}
                </div>
                {m.suggested_actions.map((act, idx) => (
                  <div key={idx} style={{ fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '5px', margin: '2px 0' }}>
                    <ChevronRight size={12} color="#06B6D4" />
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble assistant" style={{ fontStyle: 'italic', opacity: 0.8 }}>
            {language === 'hi'
              ? 'पॉलिसी दस्तावेज़ों की जांच और उद्धरण सत्यापन प्रगति पर है...'
              : 'Searching policy vector store and verifying clause citations...'}
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="quick-prompts">
        {quickPrompts.map((qp, i) => (
          <button key={i} className="prompt-chip" onClick={() => handleSend(qp)}>
            {qp}
          </button>
        ))}
      </div>

      {/* Chat Input */}
      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder={
            language === 'hi'
              ? 'पॉलिसी के बारे में कोई भी प्रश्न पूछें (उदा. कमरा किराया, को-पे, आईसीयू सीमा)...'
              : 'Ask anything about policy coverage (e.g. ICU capping, room rent, co-pay)...'
          }
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend();
          }}
        />
        <button className="chat-send-btn" onClick={() => handleSend()} disabled={loading}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};
