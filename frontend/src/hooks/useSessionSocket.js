/**
 * VoiceGuard — WebSocket Session Hook
 *
 * Manages WebSocket connection for real-time streaming:
 * - Auto-connect/reconnect
 * - Message parsing
 * - Connection state tracking
 * - Simulation command sending
 */

import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE = `ws://${window.location.hostname}:8000`;

/**
 * @param {string|null} sessionId - Session ID to connect to
 * @returns {{ messages, latestMessage, wsState, sendCommand, scoreHistory }}
 */
export function useSessionSocket(sessionId) {
  const [wsState, setWsState] = useState('disconnected'); // disconnected | connecting | connected
  const [latestMessage, setLatestMessage] = useState(null);
  const [scoreHistory, setScoreHistory] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    setWsState('connecting');

    const ws = new WebSocket(`${WS_BASE}/api/v1/sessions/${sessionId}/stream`);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsState('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'ping') return;

        if (data.type === 'connected') {
          return;
        }

        if (data.fused_score !== undefined) {
          setLatestMessage(data);
          setScoreHistory(prev => {
            const next = [...prev, data];
            // Keep last 200 data points
            return next.length > 200 ? next.slice(-200) : next;
          });
        }

        // Handle simulation complete
        if (data.type === 'simulation_complete') {
          setLatestMessage(prev => ({ ...prev, ...data, simulationComplete: true }));
        }
      } catch (e) {
        console.warn('[VoiceGuard WS] Parse error:', e);
      }
    };

    ws.onclose = () => {
      setWsState('disconnected');
      wsRef.current = null;
      // Auto-reconnect after 3 seconds
      reconnectTimer.current = setTimeout(() => {
        if (sessionId) connect();
      }, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [sessionId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  const sendCommand = useCallback((command) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command));
    }
  }, []);

  const resetHistory = useCallback(() => {
    setScoreHistory([]);
    setLatestMessage(null);
  }, []);

  return {
    wsState,
    latestMessage,
    scoreHistory,
    sendCommand,
    resetHistory,
  };
}
