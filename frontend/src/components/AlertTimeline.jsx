/**
 * VoiceGuard — AlertTimeline Component
 *
 * Bottom panel showing recent security alerts.
 * Expandable rows with sub-score details and analyst feedback.
 */

import React, { useState, useEffect } from 'react';
import { Clock, AlertCircle, CheckCircle, ChevronDown, ChevronRight, ThumbsUp, ThumbsDown } from 'lucide-react';
import { getAlerts, submitFeedback } from '../services/api.js';

function formatTime(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}

function AlertRow({ alert, onFeedback }) {
  const [expanded, setExpanded] = useState(false);

  const isFlagged = alert.risk_score >= 50;

  return (
    <div style={{
      borderBottom: '1px solid var(--border-subtle)',
    }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '8px 12px',
          cursor: 'pointer',
          transition: 'background var(--transition-fast)',
        }}
        onClick={() => setExpanded(!expanded)}
        onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        role="button"
        aria-expanded={expanded}
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        {expanded ? <ChevronDown size={12} color="var(--text-muted)" /> : <ChevronRight size={12} color="var(--text-muted)" />}

        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--text-muted)', width: '70px' }}>
          {formatTime(alert.raised_at)}
        </span>

        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--text-sm)',
          fontWeight: 600,
          width: '60px',
          color: alert.risk_score >= 70 ? 'var(--state-critical)' : alert.risk_score >= 50 ? 'var(--state-elevated)' : 'var(--state-normal)',
        }}>
          RISK {Math.round(alert.risk_score)}
        </span>

        <span className={`risk-badge ${alert.risk_state}`} style={{ width: '80px', justifyContent: 'center' }}>
          {isFlagged ? 'FLAGGED' : 'GENUINE'}
        </span>

        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', flex: 1 }}>
          {alert.transaction_type || 'General Query'}
        </span>

        {alert.analyst_feedback && (
          <span style={{
            fontSize: 'var(--text-xs)',
            color: alert.analyst_feedback === 'true_positive' ? 'var(--state-critical)' : 'var(--state-success)',
            fontWeight: 500,
          }}>
            {alert.analyst_feedback === 'true_positive' ? 'TRUE POS.' : 'FALSE POS.'}
          </span>
        )}
      </div>

      {expanded && (
        <div style={{
          padding: '8px 12px 12px 36px',
          background: 'var(--bg-panel-raised)',
          borderTop: '1px solid var(--border-subtle)',
        }}>
          <div style={{ display: 'flex', gap: '24px', marginBottom: '8px' }}>
            <div>
              <span className="label">SESSION</span>
              <span className="value" style={{ display: 'block' }}>{alert.session_id?.slice(0, 8)}</span>
            </div>
            <div>
              <span className="label">RISK SCORE</span>
              <span className="value" style={{ display: 'block' }}>{Math.round(alert.risk_score)}</span>
            </div>
            <div>
              <span className="label">TRANSACTION</span>
              <span className="value" style={{ display: 'block' }}>
                {alert.transaction_value ? `₹${alert.transaction_value.toLocaleString('en-IN')}` : '—'}
              </span>
            </div>
          </div>

          {!alert.analyst_feedback && (
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', alignSelf: 'center' }}>
                ANALYST FEEDBACK:
              </span>
              <button
                className="btn btn-ghost btn-sm"
                onClick={(e) => { e.stopPropagation(); onFeedback(alert.id, 'true_positive'); }}
              >
                <ThumbsDown size={11} /> True Positive
              </button>
              <button
                className="btn btn-ghost btn-sm"
                onClick={(e) => { e.stopPropagation(); onFeedback(alert.id, 'false_positive'); }}
              >
                <ThumbsUp size={11} /> False Positive
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AlertTimeline({ refreshTrigger }) {
  const [alerts, setAlerts] = useState([]);

  const loadAlerts = async () => {
    try {
      const res = await getAlerts({ limit: 20 });
      setAlerts(res.alerts || []);
    } catch (e) {
      // Silently handle — alerts may not be available yet
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [refreshTrigger]);

  const handleFeedback = async (alertId, feedback) => {
    try {
      await submitFeedback(alertId, { feedback });
      loadAlerts();
    } catch (e) {
      console.error('[VoiceGuard] Feedback failed:', e);
    }
  };

  return (
    <div className="panel" style={{ maxHeight: '220px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <Clock size={12} color="var(--text-muted)" />
        <span className="label">ALERT TIMELINE</span>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginLeft: 'auto' }}>
          {alerts.length} recent
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {alerts.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
            No alerts recorded
          </div>
        ) : (
          alerts.map(alert => (
            <AlertRow key={alert.id} alert={alert} onFeedback={handleFeedback} />
          ))
        )}
      </div>
    </div>
  );
}
