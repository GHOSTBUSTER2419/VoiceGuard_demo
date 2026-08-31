/**
 * VoiceGuard — SignalTraces Component
 *
 * Three live line charts showing spectral, prosody, and speaker scores.
 * Uses subdued signal colors (NOT risk-state colors).
 */

import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine } from 'recharts';

const SIGNALS = [
  { key: 'spectral_score', label: 'SPECTRAL ANALYSIS', color: '#58A6FF' },
  { key: 'prosody_score', label: 'PROSODY ANALYSIS', color: '#D2A8FF' },
  { key: 'speaker_match_score', label: 'SPEAKER CONSISTENCY', color: '#7EE787' },
];

export default function SignalTraces({ scoreHistory, threshold = 70 }) {
  // Prepare data — use window_index as x-axis
  const data = scoreHistory.map((d, i) => ({
    idx: i,
    spectral_score: d.spectral_score,
    prosody_score: d.prosody_score,
    speaker_match_score: d.speaker_match_score,
  }));

  // Show last 60 data points
  const displayData = data.slice(-60);

  return (
    <div className="panel" style={{ padding: '12px' }}>
      <span className="label" style={{ display: 'block', marginBottom: '8px' }}>
        DETECTION SIGNALS
      </span>

      <div style={{ display: 'flex', gap: '12px' }}>
        {SIGNALS.map(signal => {
          const latest = displayData.length > 0 ? displayData[displayData.length - 1][signal.key] : 0;
          return (
            <div key={signal.key} style={{ flex: 1 }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '4px',
              }}>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  color: signal.color,
                  fontWeight: 600,
                  letterSpacing: '0.04em',
                }}>
                  {signal.label}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-sm)',
                  color: latest > 60 ? 'var(--state-critical)' : latest > 40 ? 'var(--state-elevated)' : 'var(--text-secondary)',
                  fontWeight: 600,
                }}>
                  {Math.round(latest)}
                </span>
              </div>

              <ResponsiveContainer width="100%" height={80}>
                <LineChart data={displayData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                  <YAxis domain={[0, 100]} hide />
                  <XAxis dataKey="idx" hide />
                  <ReferenceLine y={threshold} stroke="var(--text-muted)" strokeDasharray="2 3" strokeWidth={0.5} />
                  <Line
                    type="monotone"
                    dataKey={signal.key}
                    stroke={signal.color}
                    strokeWidth={1.5}
                    dot={false}
                    animationDuration={200}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          );
        })}
      </div>
    </div>
  );
}
