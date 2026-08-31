/**
 * VoiceGuard — WaveformStrip Component
 *
 * Canvas-based scrolling waveform visualization.
 * In demo mode: driven by simulation state (labeled "SIMULATED AUDIO STREAM").
 * In production: would show real audio waveform (labeled "LIVE AUDIO STREAM").
 */

import React, { useRef, useEffect } from 'react';

const CANVAS_HEIGHT = 80;
const BAR_WIDTH = 3;
const BAR_GAP = 1;

export default function WaveformStrip({ isActive, riskState = 'normal', isDemo = true }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const offsetRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resizeCanvas = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = CANVAS_HEIGHT;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const getColor = () => {
      switch (riskState) {
        case 'critical': return '#E5484D';
        case 'elevated': return '#E8A33D';
        default: return '#2F6FED';
      }
    };

    const draw = () => {
      if (!canvas.width) { resizeCanvas(); }
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (!isActive) {
        // Flat line when not active
        ctx.strokeStyle = 'var(--border)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, CANVAS_HEIGHT / 2);
        ctx.lineTo(canvas.width, CANVAS_HEIGHT / 2);
        ctx.stroke();
        return;
      }

      const color = getColor();
      const numBars = Math.ceil(canvas.width / (BAR_WIDTH + BAR_GAP));
      offsetRef.current += 0.5;

      for (let i = 0; i < numBars; i++) {
        const x = i * (BAR_WIDTH + BAR_GAP);
        const phase = (i + offsetRef.current) * 0.15;

        // Multi-frequency waveform simulation
        let amplitude = (
          Math.sin(phase) * 0.3 +
          Math.sin(phase * 2.3) * 0.2 +
          Math.sin(phase * 0.7 + 1) * 0.25 +
          (Math.random() - 0.5) * 0.15
        );

        // More agitated waveform when risk is high
        if (riskState === 'critical') {
          amplitude *= 1.4;
          amplitude += (Math.random() - 0.5) * 0.15;
        } else if (riskState === 'elevated') {
          amplitude *= 1.2;
        }

        const barHeight = Math.abs(amplitude) * (CANVAS_HEIGHT * 0.7);
        const y = (CANVAS_HEIGHT - barHeight) / 2;

        ctx.fillStyle = color;
        ctx.globalAlpha = 0.4 + Math.abs(amplitude) * 0.6;
        ctx.fillRect(x, y, BAR_WIDTH, barHeight);
      }
      ctx.globalAlpha = 1;

      animRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [isActive, riskState]);

  return (
    <div className="panel" style={{ padding: '12px', position: 'relative' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
      }}>
        <span className="label">LIVE WAVEFORM</span>
        <span style={{
          fontSize: 'var(--text-xs)',
          color: isDemo ? 'var(--state-elevated)' : 'var(--state-success)',
          fontWeight: 500,
        }}>
          {isActive
            ? (isDemo ? 'SIMULATED AUDIO STREAM' : 'LIVE AUDIO STREAM')
            : 'AWAITING SIGNAL'
          }
        </span>
      </div>
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: CANVAS_HEIGHT, display: 'block' }}
        role="img"
        aria-label={isActive ? 'Audio waveform visualization' : 'No active audio signal'}
      />
    </div>
  );
}
