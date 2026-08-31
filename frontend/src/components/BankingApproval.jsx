/**
 * VoiceGuard — BankingApproval Component
 *
 * Mock banking transaction status display.
 * Shows transaction blocked → verification → approved workflow.
 * Demonstrates VoiceGuard's fraud prevention capability.
 */

import React from 'react';
import { CreditCard, ShieldCheck, ShieldX, Clock, CheckCircle } from 'lucide-react';

const styles = {
  container: {
    padding: '12px',
  },
  txCard: {
    padding: '12px',
    background: 'var(--bg-panel-raised)',
    borderRadius: 'var(--border-radius)',
    border: '1px solid var(--border)',
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '5px 0',
  },
  statusBar: {
    marginTop: '10px',
    padding: '8px 10px',
    borderRadius: 'var(--border-radius)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: 'var(--text-xs)',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
};

export default function BankingApproval({ session, riskScore = 0, riskState = 'normal', stepUpTriggered = false, stepUpVerified = false, threshold = 70 }) {
  const isBlocked = stepUpTriggered && !stepUpVerified;
  const isApproved = stepUpTriggered && stepUpVerified;
  const isPending = riskScore > 0 && riskScore < threshold;

  let statusConfig;
  if (isApproved) {
    statusConfig = {
      icon: <CheckCircle size={14} />,
      text: 'APPROVED AFTER STEP-UP AUTHENTICATION',
      bg: 'var(--state-success-bg)',
      border: 'rgba(63,185,80,0.3)',
      color: 'var(--state-success)',
    };
  } else if (isBlocked) {
    statusConfig = {
      icon: <ShieldX size={14} />,
      text: 'BLOCKED — ADDITIONAL VERIFICATION REQUIRED',
      bg: 'var(--state-critical-bg)',
      border: 'rgba(229,72,77,0.3)',
      color: 'var(--state-critical)',
    };
  } else if (riskState === 'normal' && riskScore > 0) {
    statusConfig = {
      icon: <ShieldCheck size={14} />,
      text: 'VOICE AUTHENTICITY VERIFIED',
      bg: 'var(--state-success-bg)',
      border: 'rgba(63,185,80,0.3)',
      color: 'var(--state-success)',
    };
  } else {
    statusConfig = {
      icon: <Clock size={14} />,
      text: 'AWAITING VOICE ANALYSIS',
      bg: 'var(--bg-panel-raised)',
      border: 'var(--border)',
      color: 'var(--text-muted)',
    };
  }

  return (
    <div className="panel" style={styles.container}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
        <CreditCard size={12} color="var(--text-muted)" />
        <span className="label">BANKING OPERATIONS</span>
      </div>

      <div style={styles.txCard}>
        <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', letterSpacing: '0.04em' }}>
          TRANSACTION APPROVAL
        </div>

        <div style={styles.row}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>BENEFICIARY</span>
          <span style={{ fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
            {session?.transaction_type === 'FUND_TRANSFER' ? 'ACME SUPPLIERS LTD' : '—'}
          </span>
        </div>

        <div style={styles.row}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>AMOUNT</span>
          <span style={{ fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>
            {session?.transaction_value ? `₹${session.transaction_value.toLocaleString('en-IN')}` : '—'}
          </span>
        </div>

        <div style={styles.row}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>REQUESTED BY</span>
          <span style={{ fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
            {session?.speaker_label || '—'}
          </span>
        </div>

        <div style={styles.row}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>VOICEGUARD</span>
          <span className={`risk-badge ${riskState}`}>
            {riskState.toUpperCase()} — {Math.round(riskScore)}
          </span>
        </div>

        {/* Transaction Status */}
        <div style={{
          ...styles.statusBar,
          background: statusConfig.bg,
          border: `1px solid ${statusConfig.border}`,
          color: statusConfig.color,
        }}>
          {statusConfig.icon}
          {statusConfig.text}
        </div>
      </div>
    </div>
  );
}
