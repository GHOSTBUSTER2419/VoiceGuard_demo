/**
 * VoiceGuard — Main Application
 *
 * SOC / Fraud Operations Console layout.
 * Orchestrates all components, WebSocket connection, and demo simulation.
 */

import React, { useState, useCallback, useEffect } from 'react';
import TopBar from './components/TopBar.jsx';
import MetadataSidebar from './components/MetadataSidebar.jsx';
import WaveformStrip from './components/WaveformStrip.jsx';
import SignalTraces from './components/SignalTraces.jsx';
import ExplainabilityPanel from './components/ExplainabilityPanel.jsx';
import RiskGauge from './components/RiskGauge.jsx';
import ThresholdControl from './components/ThresholdControl.jsx';
import AlertTimeline from './components/AlertTimeline.jsx';
import BankingApproval from './components/BankingApproval.jsx';
import StepUpOverlay from './components/StepUpOverlay.jsx';
import { useSessionSocket } from './hooks/useSessionSocket.js';
import { triggerSimulation, getOrgConfig, checkTransaction, getDemoStatus } from './services/api.js';

export default function App() {
  // --- State ---
  const [sessionId, setSessionId] = useState(null);
  const [session, setSession] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simType, setSimType] = useState(null);
  const [modelMode, setModelMode] = useState('demo');
  const [threshold, setThreshold] = useState(70);
  const [workflow, setWorkflow] = useState('otp');
  const [alertRefresh, setAlertRefresh] = useState(0);

  // Step-up state
  const [showStepUp, setShowStepUp] = useState(false);
  const [stepUpTriggered, setStepUpTriggered] = useState(false);
  const [stepUpVerified, setStepUpVerified] = useState(false);
  const [transactionId, setTransactionId] = useState(null);

  // WebSocket connection
  const { wsState, latestMessage, scoreHistory, sendCommand, resetHistory } = useSessionSocket(sessionId);

  // --- Load initial config ---
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const [config, status] = await Promise.all([
          getOrgConfig('default'),
          getDemoStatus(),
        ]);
        setThreshold(config.risk_threshold);
        setWorkflow(config.workflow);
        setModelMode(status.mode);
      } catch (e) {
        // Backend may not be ready yet — use defaults
      }
    };
    loadConfig();
  }, []);

  // --- React to step-up signals from backend ---
  useEffect(() => {
    if (!latestMessage) return;

    // Backend is authoritative for step-up decisions
    if (latestMessage.step_up_required && !stepUpTriggered && !stepUpVerified) {
      setStepUpTriggered(true);

      // Check transaction via banking API
      checkTransaction({
        transaction_type: session?.transaction_type || 'FUND_TRANSFER',
        amount: session?.transaction_value || 250000,
        risk_score: latestMessage.fused_score,
        threshold: latestMessage.threshold,
        session_id: sessionId,
      }).then(result => {
        setTransactionId(result.transaction_id);
        if (result.step_up_required) {
          setShowStepUp(true);
        }
      }).catch(() => {
        // Still show overlay even if banking API fails
        setShowStepUp(true);
      });
    }

    // Handle simulation complete
    if (latestMessage.simulationComplete) {
      setIsSimulating(false);
      setAlertRefresh(prev => prev + 1);
    }
  }, [latestMessage, stepUpTriggered, stepUpVerified, session, sessionId]);

  // --- Simulation handler ---
  const handleSimulate = useCallback(async (type) => {
    try {
      // Reset state
      resetHistory();
      setStepUpTriggered(false);
      setStepUpVerified(false);
      setShowStepUp(false);
      setTransactionId(null);
      setSimType(type);

      // Create session via API
      const result = await triggerSimulation({
        type,
        org_id: 'default',
        transaction_type: type === 'cloned' ? 'FUND_TRANSFER' : 'GENERAL_QUERY',
        transaction_value: type === 'cloned' ? 250000 : 0,
        speaker_label: type === 'cloned' ? 'CFO - Rajesh Kumar' : 'Priya Sharma',
        language: 'en',
      });

      const newSession = {
        id: result.session_id,
        org_id: 'default',
        origin: '+91 ******4821',
        speaker_label: result.speaker_label,
        language: 'en',
        accent_profile: 'Indian English',
        transaction_type: result.transaction_type,
        transaction_value: result.transaction_value,
        known_contact: type === 'genuine',
        is_demo: true,
      };

      setSession(newSession);
      setSessionId(result.session_id);
      setIsSimulating(true);

      // Wait for WebSocket to connect, then start simulation
      setTimeout(() => {
        sendCommand({
          command: 'start_simulation',
          type: type,
          transaction_type: newSession.transaction_type,
        });
      }, 500);

    } catch (e) {
      console.error('[VoiceGuard] Simulation failed:', e);
      setIsSimulating(false);
    }
  }, [resetHistory, sendCommand]);

  const handleStop = useCallback(() => {
    sendCommand({ command: 'stop' });
    setIsSimulating(false);
  }, [sendCommand]);

  const handleStepUpVerified = useCallback(() => {
    setShowStepUp(false);
    setStepUpVerified(true);
  }, []);

  const handleStepUpCancel = useCallback(() => {
    setShowStepUp(false);
  }, []);

  const handleConfigUpdate = useCallback(({ threshold: t, workflow: w }) => {
    setThreshold(t);
    setWorkflow(w);
  }, []);

  // --- Derived state ---
  const riskState = latestMessage?.risk_state || 'normal';
  const fusedScore = latestMessage?.fused_score || 0;
  const trend = latestMessage?.trend || 0;
  const reasons = latestMessage?.reasons || [];
  const latencyMs = latestMessage?.latency_ms || 0;
  const isActive = isSimulating || (latestMessage && !latestMessage.simulationComplete);

  return (
    <div className="app-layout">
      {/* Top Bar */}
      <TopBar
        wsState={wsState}
        modelMode={modelMode}
        isSimulating={isSimulating}
        onSimulate={handleSimulate}
        onStop={handleStop}
      />

      {/* Left Sidebar — Call Metadata */}
      <MetadataSidebar
        session={session}
        isActive={isActive}
        riskState={riskState}
      />

      {/* Center — Live Signal Area */}
      <div className="app-center">
        <WaveformStrip
          isActive={isActive}
          riskState={riskState}
          isDemo={true}
        />

        <SignalTraces
          scoreHistory={scoreHistory}
          threshold={threshold}
        />

        <ExplainabilityPanel reasons={reasons} />

        {/* Alert Timeline at bottom of center */}
        <AlertTimeline refreshTrigger={alertRefresh} />
      </div>

      {/* Right Column — Risk Gauge + Policy + Banking */}
      <div className="app-right">
        <RiskGauge
          score={fusedScore}
          riskState={riskState}
          trend={trend}
          threshold={threshold}
        />

        <ThresholdControl
          threshold={threshold}
          workflow={workflow}
          onUpdate={handleConfigUpdate}
        />

        <BankingApproval
          session={session}
          riskScore={fusedScore}
          riskState={riskState}
          stepUpTriggered={stepUpTriggered}
          stepUpVerified={stepUpVerified}
          threshold={threshold}
        />

        {/* Latency indicator */}
        {latencyMs > 0 && (
          <div className="panel" style={{ padding: '8px 12px', textAlign: 'center' }}>
            <span className="label">PROCESSING LATENCY</span>
            <span style={{
              display: 'block',
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-sm)',
              color: latencyMs > 300 ? 'var(--state-elevated)' : 'var(--text-secondary)',
              marginTop: '2px',
            }}>
              {latencyMs.toFixed(1)} ms
            </span>
          </div>
        )}
      </div>

      {/* Step-Up Verification Overlay */}
      <StepUpOverlay
        visible={showStepUp}
        riskScore={fusedScore}
        threshold={threshold}
        transactionType={session?.transaction_type}
        transactionValue={session?.transaction_value}
        workflow={workflow}
        transactionId={transactionId}
        onVerified={handleStepUpVerified}
        onCancel={handleStepUpCancel}
      />
    </div>
  );
}
