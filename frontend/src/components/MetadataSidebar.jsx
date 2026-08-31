/**
 * VoiceGuard — MetadataSidebar Component
 *
 * Left sidebar displaying call metadata:
 * Session ID, org, call origin, duration, speaker, language, transaction details.
 */

import React, { useState, useEffect } from 'react';
import { Phone, User, Globe, Clock, Building, CreditCard, Hash, Shield } from 'lucide-react';

const styles = {
  sidebar: {
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    background: 'var(--bg-panel)',
  },
  sectionTitle: {
    fontSize: 'var(--text-xs)',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: 'var(--text-muted)',
    marginTop: '16px',
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '6px 0',
    borderBottom: '1px solid var(--border-subtle)',
  },
  label: {
    fontSize: 'var(--text-xs)',
    color: 'var(--text-muted)',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
  value: {
    fontFamily: 'var(--font-mono)',
    fontSize: 'var(--text-xs)',
    color: 'var(--text-primary)',
    textAlign: 'right',
    maxWidth: '160px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  callStatus: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 12px',
    borderRadius: 'var(--border-radius)',
    marginBottom: '8px',
  },
};

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function formatCurrency(value) {
  if (!value) return '—';
  return '₹' + value.toLocaleString('en-IN');
}

export default function MetadataSidebar({ session, isActive, riskState }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!isActive) { setElapsed(0); return; }
    const interval = setInterval(() => setElapsed(e => e + 1), 1000);
    return () => clearInterval(interval);
  }, [isActive]);

  const statusColor = isActive ? 'var(--state-success)' : 'var(--text-muted)';
  const statusBg = isActive ? 'var(--state-success-bg)' : 'var(--bg-panel-raised)';

  return (
    <div style={styles.sidebar} className="app-sidebar" role="complementary" aria-label="Call Metadata">
      {/* Call Status */}
      <div style={{ ...styles.callStatus, background: statusBg, border: `1px solid ${isActive ? 'rgba(63,185,80,0.3)' : 'var(--border)'}` }}>
        <span className={`status-dot ${isActive ? 'online' : ''}`} />
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: statusColor, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {isActive ? 'CALL ACTIVE' : 'NO ACTIVE CALL'}
        </span>
      </div>

      {/* Session Info */}
      <div style={styles.sectionTitle}>
        <Hash size={11} /> SESSION
      </div>

      <MetaRow label="SESSION ID" value={session?.id?.slice(0, 8) || '—'} />
      <MetaRow label="ORGANIZATION" value={session?.org_id || 'default'} />
      <MetaRow label="CALL DURATION" value={isActive ? formatDuration(elapsed) : '—'} />

      {/* Caller Info */}
      <div style={styles.sectionTitle}>
        <User size={11} /> CALLER
      </div>

      <MetaRow label="CALL ORIGIN" value={session?.origin || '+91 ******4821'} />
      <MetaRow label="SPEAKER" value={session?.speaker_label || '—'} />
      <MetaRow label="KNOWN CONTACT" value={session?.known_contact ? 'YES' : 'NO'} />

      {/* Language */}
      <div style={styles.sectionTitle}>
        <Globe size={11} /> LANGUAGE
      </div>

      <MetaRow label="LANGUAGE" value={session?.language?.toUpperCase() || 'EN'} />
      <MetaRow label="ACCENT" value={session?.accent_profile || 'Indian English'} />

      {/* Transaction */}
      <div style={styles.sectionTitle}>
        <CreditCard size={11} /> TRANSACTION
      </div>

      <MetaRow label="TYPE" value={session?.transaction_type || '—'} />
      <MetaRow label="VALUE" value={formatCurrency(session?.transaction_value)} />

      {/* Demo indicator */}
      {session?.is_demo && (
        <div style={{
          marginTop: '16px',
          padding: '8px 12px',
          background: 'var(--state-elevated-bg)',
          border: '1px solid rgba(232,163,61,0.3)',
          borderRadius: 'var(--border-radius)',
          textAlign: 'center',
        }}>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--state-elevated)', letterSpacing: '0.06em' }}>
            DEMO MODE — SIMULATED AUDIO
          </span>
        </div>
      )}
    </div>
  );
}

function MetaRow({ label, value }) {
  return (
    <div style={styles.row}>
      <span style={styles.label}>{label}</span>
      <span style={styles.value}>{value}</span>
    </div>
  );
}
