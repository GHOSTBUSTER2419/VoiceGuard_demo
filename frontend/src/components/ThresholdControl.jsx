/**
 * VoiceGuard — ThresholdControl Component
 *
 * Configurable risk threshold slider and workflow selector.
 * Changes are persisted through the API — backend is authoritative.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Settings, Save } from 'lucide-react';
import { updateOrgConfig } from '../services/api.js';

export default function ThresholdControl({ threshold: initialThreshold = 70, workflow: initialWorkflow = 'otp', onUpdate }) {
  const [threshold, setThreshold] = useState(initialThreshold);
  const [workflow, setWorkflow] = useState(initialWorkflow);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    setThreshold(initialThreshold);
    setWorkflow(initialWorkflow);
  }, [initialThreshold, initialWorkflow]);

  const handleThresholdChange = (e) => {
    setThreshold(Number(e.target.value));
    setDirty(true);
  };

  const handleWorkflowChange = (e) => {
    setWorkflow(e.target.value);
    setDirty(true);
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      await updateOrgConfig('default', { risk_threshold: threshold, workflow });
      setDirty(false);
      if (onUpdate) onUpdate({ threshold, workflow });
    } catch (err) {
      console.error('[VoiceGuard] Config update failed:', err);
    } finally {
      setSaving(false);
    }
  }, [threshold, workflow, onUpdate]);

  return (
    <div className="panel" style={{ padding: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
        <Settings size={12} color="var(--text-muted)" />
        <span className="label">POLICY CONFIGURATION</span>
      </div>

      {/* Threshold Slider */}
      <div style={{ marginBottom: '12px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '6px',
        }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
            RISK THRESHOLD
          </span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--text-md)',
            fontWeight: 600,
            color: threshold > 80 ? 'var(--state-critical)' : threshold < 50 ? 'var(--state-elevated)' : 'var(--text-primary)',
          }}>
            {threshold}
          </span>
        </div>

        <input
          type="range"
          min={30}
          max={95}
          value={threshold}
          onChange={handleThresholdChange}
          aria-label="Risk threshold"
          style={{ width: '100%' }}
        />

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: 'var(--text-xs)',
          color: 'var(--text-muted)',
          marginTop: '2px',
        }}>
          <span>Strict (30)</span>
          <span>Lenient (95)</span>
        </div>
      </div>

      {/* Workflow Selector */}
      <div style={{ marginBottom: '12px' }}>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
          STEP-UP WORKFLOW
        </span>
        <select
          value={workflow}
          onChange={handleWorkflowChange}
          aria-label="Step-up verification workflow"
          style={{ width: '100%' }}
        >
          <option value="otp">OTP Verification</option>
          <option value="callback">Callback Verification</option>
          <option value="supervisor">Supervisor Approval</option>
        </select>
      </div>

      {/* Save Button */}
      {dirty && (
        <button
          className="btn btn-primary btn-sm w-full"
          onClick={handleSave}
          disabled={saving}
          style={{ justifyContent: 'center' }}
        >
          <Save size={12} />
          {saving ? 'SAVING...' : 'SAVE POLICY'}
        </button>
      )}
    </div>
  );
}
