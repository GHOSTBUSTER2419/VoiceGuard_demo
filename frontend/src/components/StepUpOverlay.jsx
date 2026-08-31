/**
 * VoiceGuard — StepUpOverlay Component
 *
 * Security intervention modal triggered when risk >= threshold.
 * Supports OTP, callback, and supervisor verification workflows.
 * Backend is authoritative — frontend displays, backend decides.
 */

import React, { useState } from 'react';
import { ShieldAlert, Send, Phone, UserCheck, X, CheckCircle, Lock } from 'lucide-react';
import { requestStepUp, verifyTransaction } from '../services/api.js';

const styles = {
  modal: {
    background: 'var(--bg-panel)',
    border: '1px solid var(--state-critical)',
    borderRadius: 'var(--border-radius-lg)',
    width: '420px',
    maxWidth: '90vw',
    overflow: 'hidden',
  },
  header: {
    background: 'var(--state-critical-bg)',
    borderBottom: '1px solid rgba(229, 72, 77, 0.3)',
    padding: '16px 20px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  body: {
    padding: '20px',
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 0',
    borderBottom: '1px solid var(--border-subtle)',
  },
  actions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginTop: '16px',
  },
  otpInput: {
    display: 'flex',
    gap: '8px',
    marginTop: '12px',
  },
};

export default function StepUpOverlay({
  visible,
  riskScore = 0,
  threshold = 70,
  transactionType,
  transactionValue,
  workflow = 'otp',
  transactionId,
  onVerified,
  onCancel,
}) {
  const [stage, setStage] = useState('initial'); // initial | choose_number | otp_sent | verifying | verified | escalated
  const [otpValue, setOtpValue] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');

  if (!visible) return null;

  const handleInitiateOTP = () => {
    setStage('choose_number');
    setError('');
  };

  const handleSendOTP = async () => {
    if (!phoneNumber.trim()) {
      setError('Please enter a phone number');
      return;
    }
    try {
      await requestStepUp({ transaction_id: transactionId, method: 'otp', phone: phoneNumber });
      setStage('otp_sent');
      setError('');
    } catch (e) {
      setError('Failed to send OTP');
    }
  };

  const handleVerify = async () => {
    if (!otpValue.trim()) return;
    setStage('verifying');
    try {
      const code = otpValue.trim() || '123456';
      const result = await verifyTransaction({ transaction_id: transactionId, verification_code: code });
      if (result.status === 'approved_after_stepup') {
        setStage('verified');
        setTimeout(() => onVerified && onVerified(), 1500);
      } else {
        setError('Verification failed. Try again.');
        setStage('otp_sent');
      }
    } catch (e) {
      setError('Verification failed');
      setStage('otp_sent');
    }
  };

  const handleEscalate = async () => {
    try {
      await requestStepUp({ transaction_id: transactionId, method: 'supervisor' });
      setStage('escalated');
    } catch (e) {
      setError('Escalation failed');
    }
  };

  const formatValue = (val) => val ? `₹${val.toLocaleString('en-IN')}` : '—';

  return (
    <div className="overlay-backdrop" role="dialog" aria-modal="true" aria-label="Security intervention required">
      <div style={styles.modal}>
        {/* Header */}
        <div style={styles.header}>
          <ShieldAlert size={20} color="var(--state-critical)" />
          <div>
            <div style={{ fontSize: 'var(--text-md)', fontWeight: 700, color: 'var(--state-critical)' }}>
              SECURITY INTERVENTION
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
              HIGH IMPERSONATION RISK DETECTED
            </div>
          </div>
        </div>

        {/* Body */}
        <div style={styles.body}>
          {stage === 'verified' ? (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <CheckCircle size={48} color="var(--state-success)" style={{ marginBottom: '12px' }} />
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--state-success)' }}>
                STEP-UP VERIFIED
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Transaction can proceed
              </div>
            </div>
          ) : stage === 'escalated' ? (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <UserCheck size={48} color="var(--state-elevated)" style={{ marginBottom: '12px' }} />
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--state-elevated)' }}>
                ESCALATED TO SUPERVISOR
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Awaiting manual review
              </div>
              <button className="btn btn-primary btn-sm" style={{ marginTop: '16px' }} onClick={() => { setStage('verified'); setTimeout(() => onVerified && onVerified(), 1500); }}>
                <CheckCircle size={12} /> APPROVE (DEMO)
              </button>
            </div>
          ) : (
            <>
              {/* Risk Details */}
              <div style={styles.row}>
                <span className="label">RISK SCORE</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--state-critical)' }}>
                  {Math.round(riskScore)} / 100
                </span>
              </div>
              <div style={styles.row}>
                <span className="label">THRESHOLD</span>
                <span className="value">{threshold} / 100</span>
              </div>
              <div style={styles.row}>
                <span className="label">CONFIDENCE</span>
                <span className="value">High</span>
              </div>
              <div style={styles.row}>
                <span className="label">TRANSACTION</span>
                <span className="value">{formatValue(transactionValue)} {transactionType}</span>
              </div>

              {/* Reason */}
              <div style={{
                marginTop: '12px',
                padding: '10px',
                background: 'var(--state-critical-bg)',
                borderRadius: 'var(--border-radius)',
                border: '1px solid rgba(229,72,77,0.2)',
                fontSize: 'var(--text-xs)',
                color: 'var(--text-secondary)',
              }}>
                <Lock size={12} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                Voice authenticity signals disagree with enrolled identity. Transaction requires additional verification.
              </div>

              {/* Choose Number Section */}
              {stage === 'choose_number' && (
                <div style={{ marginTop: '12px' }}>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    ENTER NUMBER FOR OTP VERIFICATION
                  </div>
                  <div style={styles.otpInput}>
                    <input
                      type="text"
                      placeholder="Enter phone number"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      style={{ flex: 1 }}
                      aria-label="Phone number"
                      autoFocus
                      onKeyDown={(e) => e.key === 'Enter' && handleSendOTP()}
                    />
                    <button className="btn btn-primary btn-sm" onClick={handleSendOTP}>
                      SEND
                    </button>
                  </div>
                  <button className="btn btn-ghost w-full" onClick={() => { setStage('initial'); setError(''); }} style={{ justifyContent: 'center', marginTop: '8px' }}>
                    <X size={14} /> CANCEL
                  </button>
                </div>
              )}

              {/* OTP Section */}
              {stage === 'otp_sent' && (
                <div style={{ marginTop: '12px' }}>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--state-success)', marginBottom: '8px' }}>
                    OTP SENT TO {phoneNumber || '+91 ******4821'}
                  </div>
                  <div style={styles.otpInput}>
                    <input
                      type="text"
                      placeholder="Enter OTP (demo: 123456)"
                      value={otpValue}
                      onChange={(e) => setOtpValue(e.target.value)}
                      style={{ flex: 1 }}
                      aria-label="OTP code"
                      autoFocus
                      onKeyDown={(e) => e.key === 'Enter' && handleVerify()}
                    />
                    <button className="btn btn-success btn-sm" onClick={handleVerify}>
                      VERIFY
                    </button>
                  </div>
                </div>
              )}

              {error && (
                <div style={{ marginTop: '8px', fontSize: 'var(--text-xs)', color: 'var(--state-critical)' }}>
                  {error}
                </div>
              )}

              {/* Actions */}
              <div style={styles.actions}>
                {stage === 'initial' && (
                  <>
                    <button className="btn btn-primary w-full" onClick={handleInitiateOTP} style={{ justifyContent: 'center' }}>
                      <Send size={14} /> SEND OTP VERIFICATION
                    </button>
                    <button className="btn btn-warning w-full" onClick={handleEscalate} style={{ justifyContent: 'center' }}>
                      <UserCheck size={14} /> ESCALATE TO SUPERVISOR
                    </button>
                    <button className="btn btn-ghost w-full" onClick={onCancel} style={{ justifyContent: 'center' }}>
                      <X size={14} /> CANCEL TRANSACTION
                    </button>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
