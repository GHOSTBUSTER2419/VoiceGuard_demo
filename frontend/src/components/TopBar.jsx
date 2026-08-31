/**
 * VoiceGuard — TopBar Component
 *
 * Displays: logo, system status, WebSocket status, model mode, demo controls.
 */

import React from 'react';
import { Shield, Wifi, WifiOff, Activity, Radio } from 'lucide-react';

const styles = {
  topbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 16px',
    background: 'var(--bg-panel)',
    borderBottom: '1px solid var(--border)',
    height: 'var(--topbar-height)',
    zIndex: 100,
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  logoText: {
    fontFamily: 'var(--font-sans)',
    fontSize: 'var(--text-md)',
    fontWeight: 700,
    color: 'var(--text-primary)',
    letterSpacing: '0.04em',
  },
  subtitle: {
    fontSize: 'var(--text-xs)',
    color: 'var(--text-muted)',
    fontWeight: 400,
    letterSpacing: '0.02em',
  },
  statusGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  statusItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: 'var(--text-xs)',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
};

export default function TopBar({ wsState, modelMode, isSimulating, onSimulate, onStop }) {
  const wsConnected = wsState === 'connected';

  return (
    <div style={styles.topbar} className="app-topbar" role="banner">
      {/* Left: Logo + Status */}
      <div style={styles.left}>
        <div style={styles.logo}>
          <Shield size={18} color="var(--state-normal)" />
          <div>
            <span style={styles.logoText}>VOICEGUARD</span>
            <span style={{ ...styles.subtitle, marginLeft: 8 }}>REAL-TIME VOICE SECURITY</span>
          </div>
        </div>

        <div style={styles.statusGroup}>
          <div style={styles.statusItem}>
            <span className={`status-dot ${wsConnected ? 'online' : 'offline'}`} />
            <span style={{ color: wsConnected ? 'var(--state-success)' : 'var(--state-critical)' }}>
              {wsConnected ? 'SYSTEM ONLINE' : 'OFFLINE'}
            </span>
          </div>

          <div style={styles.statusItem}>
            {wsConnected ? <Wifi size={12} color="var(--state-success)" /> : <WifiOff size={12} color="var(--state-critical)" />}
            <span style={{ color: wsConnected ? 'var(--text-secondary)' : 'var(--state-critical)' }}>
              {wsConnected ? 'WS CONNECTED' : 'WS DISCONNECTED'}
            </span>
          </div>

          <div style={styles.statusItem}>
            <Activity size={12} color="var(--text-muted)" />
            <span style={{ color: 'var(--text-muted)' }}>
              MODEL: {modelMode === 'demo' ? 'DEMO' : 'PRODUCTION'}
            </span>
          </div>
        </div>
      </div>

      {/* Right: Demo Controls */}
      <div style={styles.right}>
        {isSimulating && (
          <button className="btn btn-ghost btn-sm" onClick={onStop} aria-label="Stop simulation">
            STOP
          </button>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => onSimulate('genuine')}
          disabled={isSimulating}
          aria-label="Simulate genuine call"
        >
          <Radio size={12} />
          SIMULATE GENUINE CALL
        </button>
        <button
          className="btn btn-danger btn-sm"
          onClick={() => onSimulate('cloned')}
          disabled={isSimulating}
          aria-label="Simulate cloned call"
        >
          <Shield size={12} />
          SIMULATE CLONED CALL
        </button>
      </div>
    </div>
  );
}
