import React, { useState } from 'react';
import { loginUser, registerUser, saveSession } from '../api/auth';

export const LoginPage: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const auth = mode === 'login' ? await loginUser(email, password) : await registerUser(email, password, name);
      saveSession(auth);
      onSuccess();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
      <form onSubmit={submit} className="glass-panel" style={{ width: '340px', padding: '28px' }}>
        <h2 style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)', marginBottom: '4px' }}>CareWise</h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
          {mode === 'login' ? 'Log in to your account' : 'Create your account'}
        </p>

        {mode === 'register' && (
          <input className="filter-select" style={{ width: '100%', marginBottom: '10px' }} placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} required />
        )}
        <input className="filter-select" style={{ width: '100%', marginBottom: '10px' }} type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="filter-select" style={{ width: '100%', marginBottom: '14px' }} type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />

        {error && <div style={{ color: '#dc2626', fontSize: '0.78rem', marginBottom: '10px' }}>{error}</div>}

        <button className="btn-primary" style={{ width: '100%' }} disabled={loading}>
          {loading ? 'Please wait...' : mode === 'login' ? 'Log In' : 'Create Account'}
        </button>

        <div style={{ textAlign: 'center', marginTop: '14px', fontSize: '0.78rem' }}>
          <button type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')} style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer' }}>
            {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
          </button>
        </div>
      </form>
    </div>
  );
};
