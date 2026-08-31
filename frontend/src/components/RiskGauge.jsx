/**
 * VoiceGuard — RiskGauge Component
 *
 * Large SVG arc gauge showing fused risk score.
 * Color follows risk state. Animates smoothly.
 * Shows trend indicator and risk state label.
 */

import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const SIZE = 200;
const STROKE = 12;
const RADIUS = (SIZE - STROKE) / 2;
const CENTER = SIZE / 2;
// Arc from 135° to 405° (270° sweep)
const START_ANGLE = 135;
const END_ANGLE = 405;
const SWEEP = END_ANGLE - START_ANGLE;

function polarToCartesian(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

function getRiskColor(state) {
  switch (state) {
    case 'critical': return 'var(--state-critical)';
    case 'elevated': return 'var(--state-elevated)';
    default: return 'var(--state-normal)';
  }
}

function getRiskLabel(state) {
  switch (state) {
    case 'critical': return 'CRITICAL RISK';
    case 'elevated': return 'ELEVATED RISK';
    default: return 'NORMAL';
  }
}

export default function RiskGauge({ score = 0, riskState = 'normal', trend = 0, threshold = 70 }) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const scoreAngle = START_ANGLE + (clampedScore / 100) * SWEEP;
  const thresholdAngle = START_ANGLE + (threshold / 100) * SWEEP;

  const bgArc = describeArc(CENTER, CENTER, RADIUS, START_ANGLE, END_ANGLE);
  const valueArc = describeArc(CENTER, CENTER, RADIUS, START_ANGLE, scoreAngle);
  const color = getRiskColor(riskState);

  const thresholdPos = polarToCartesian(CENTER, CENTER, RADIUS, thresholdAngle);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        IMPERSONATION RISK
      </div>

      <svg width={SIZE} height={SIZE * 0.75} viewBox={`0 0 ${SIZE} ${SIZE * 0.8}`} role="img" aria-label={`Risk score: ${Math.round(clampedScore)}, ${getRiskLabel(riskState)}`}>
        {/* Background arc */}
        <path d={bgArc} fill="none" stroke="var(--border)" strokeWidth={STROKE} strokeLinecap="round" />

        {/* Value arc */}
        <path
          d={valueArc}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          style={{ transition: 'all 300ms ease' }}
        />

        {/* Threshold marker */}
        <circle
          cx={thresholdPos.x}
          cy={thresholdPos.y}
          r={3}
          fill="var(--text-muted)"
        />

        {/* Score text */}
        <text
          x={CENTER}
          y={CENTER - 6}
          textAnchor="middle"
          fill={color}
          fontSize="42"
          fontFamily="var(--font-mono)"
          fontWeight="700"
          style={{ transition: 'fill 300ms ease' }}
        >
          {Math.round(clampedScore)}
        </text>

        {/* Label */}
        <text
          x={CENTER}
          y={CENTER + 18}
          textAnchor="middle"
          fill={color}
          fontSize="10"
          fontFamily="var(--font-sans)"
          fontWeight="600"
          letterSpacing="0.1em"
          style={{ transition: 'fill 300ms ease' }}
        >
          {getRiskLabel(riskState)}
        </text>
      </svg>

      {/* Trend */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        fontSize: 'var(--text-xs)',
        color: trend > 5 ? 'var(--state-critical)' : trend < -5 ? 'var(--state-success)' : 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
      }}>
        {trend > 2 ? <TrendingUp size={12} /> : trend < -2 ? <TrendingDown size={12} /> : <Minus size={12} />}
        <span>
          {trend > 0 ? '+' : ''}{trend.toFixed(1)} / 3s
        </span>
      </div>

      {/* Threshold indicator */}
      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
        Threshold: {threshold}
      </div>
    </div>
  );
}
