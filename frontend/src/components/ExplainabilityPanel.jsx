/**
 * VoiceGuard — ExplainabilityPanel Component
 *
 * "Why is VoiceGuard concerned?" — shows active detection reasons.
 * Collapsible cards with severity indicators.
 * Uses lucide-react icons, not emoji.
 */

import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, AlertCircle, XCircle, ChevronDown, ChevronRight, Info } from 'lucide-react';

function getSeverityIcon(severity) {
  switch (severity) {
    case 'ok': return <CheckCircle size={14} color="var(--severity-ok)" />;
    case 'low': return <AlertTriangle size={14} color="var(--severity-low)" />;
    case 'medium': return <AlertTriangle size={14} color="var(--severity-medium)" />;
    case 'high': return <AlertCircle size={14} color="var(--severity-high)" />;
    case 'critical': return <XCircle size={14} color="var(--severity-critical)" />;
    default: return <Info size={14} color="var(--severity-info)" />;
  }
}

function getSeverityColor(severity) {
  switch (severity) {
    case 'ok': return 'var(--severity-ok)';
    case 'low': return 'var(--severity-low)';
    case 'medium': return 'var(--severity-medium)';
    case 'high': return 'var(--severity-high)';
    case 'critical': return 'var(--severity-critical)';
    default: return 'var(--severity-info)';
  }
}

function ReasonCard({ reason }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        padding: '8px 10px',
        borderLeft: `2px solid ${getSeverityColor(reason.severity)}`,
        background: 'var(--bg-panel-raised)',
        borderRadius: '0 var(--border-radius) var(--border-radius) 0',
        marginBottom: '4px',
        cursor: reason.description ? 'pointer' : 'default',
      }}
      onClick={() => reason.description && setExpanded(!expanded)}
      role="button"
      aria-expanded={expanded}
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && reason.description && setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {getSeverityIcon(reason.severity)}
        <span style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--text-primary)',
          fontWeight: 500,
          flex: 1,
        }}>
          {reason.title}
        </span>
        {reason.description && (
          expanded ? <ChevronDown size={12} color="var(--text-muted)" /> : <ChevronRight size={12} color="var(--text-muted)" />
        )}
      </div>

      {expanded && reason.description && (
        <div style={{
          marginTop: '6px',
          paddingLeft: '22px',
          fontSize: 'var(--text-xs)',
          color: 'var(--text-secondary)',
          lineHeight: 1.5,
        }}>
          {reason.description}
          {reason.signal_source && (
            <span style={{ display: 'block', marginTop: '4px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
              Source: {reason.signal_source}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default function ExplainabilityPanel({ reasons = [] }) {
  if (reasons.length === 0) {
    return (
      <div className="panel" style={{ padding: '12px' }}>
        <span className="label">EXPLAINABILITY</span>
        <div style={{ padding: '16px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
          No active signals — awaiting analysis
        </div>
      </div>
    );
  }

  const concerns = reasons.filter(r => r.severity !== 'ok');
  const healthy = reasons.filter(r => r.severity === 'ok');

  return (
    <div className="panel" style={{ padding: '12px' }}>
      <span className="label" style={{ display: 'block', marginBottom: '8px' }}>
        {concerns.length > 0 ? 'WHY IS VOICEGUARD CONCERNED?' : 'VOICE AUTHENTICITY STATUS'}
      </span>

      {healthy.map((r, i) => <ReasonCard key={r.id || i} reason={r} />)}
      {concerns.map((r, i) => <ReasonCard key={r.id || i} reason={r} />)}
    </div>
  );
}
