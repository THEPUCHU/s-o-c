import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AgentTopologyGraph from './components/AgentTopologyGraph';
import AlertStream from './components/AlertStream';
import InvestigationCenter from './components/InvestigationCenter';
import DigitalSocTwin from './components/DigitalSocTwin';
import ContainmentSOAR from './components/ContainmentSOAR';
import ThreatHunterPlayground from './components/ThreatHunterPlayground';
import MemoryExplorer from './components/MemoryExplorer';
import ExecutiveReportModal from './components/ExecutiveReportModal';
import BenchmarkReportModal from './components/BenchmarkReportModal';

import { ATTACK_SCENARIOS } from './data/mockData';
import { AgentOrchestrator } from './services/agentEngine';

export default function App() {
  const [activeScenario, setActiveScenario] = useState(ATTACK_SCENARIOS[0]);
  const [activeTab, setActiveTab] = useState('investigation');
  const [logs, setLogs] = useState([]);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [finalReport, setFinalReport] = useState(null);
  const [activeAgentId, setActiveAgentId] = useState('coordinator');
  const [currentPhase, setCurrentPhase] = useState('STANDBY');

  const [isReportOpen, setIsReportOpen] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);

  // Initialize Agent Orchestrator
  const handleStartInvestigation = async () => {
    setLogs([]);
    setIsComplete(false);
    setFinalReport(null);
    setIsInvestigating(true);

    const orchestrator = new AgentOrchestrator((update) => {
      setLogs(update.logs);
      if (update.currentStep) {
        setActiveAgentId(update.currentStep.agentId);
        setCurrentPhase(update.currentStep.phase);
      }
      if (update.isComplete) {
        setIsInvestigating(false);
        setIsComplete(true);
        setFinalReport(update.finalReport);
      }
    });

    await orchestrator.runInvestigation(activeScenario);
  };

  const pendingApprovalsCount = activeScenario.recommendedActions.filter(a => a.hitlRequired).length;

  return (
    <div className="min-h-screen bg-[#060911] text-slate-100 font-sans flex flex-col">
      {/* Header Bar */}
      <Header
        activeScenario={activeScenario}
        onSelectScenario={(sc) => {
          setActiveScenario(sc);
          setLogs([]);
          setIsComplete(false);
          setFinalReport(null);
        }}
        attackScenarios={ATTACK_SCENARIOS}
        isInvestigating={isInvestigating}
        onOpenReport={() => setIsReportOpen(true)}
        onOpenBenchmark={() => setIsBenchmarkOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingApprovalsCount={pendingApprovalsCount}
      />

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-[1700px] w-full mx-auto p-4 flex flex-col gap-4">
        
        {/* Top Multi-Agent Topology Visualizer Graph */}
        <AgentTopologyGraph
          activeAgentId={activeAgentId}
          currentPhase={currentPhase}
          logs={logs}
        />

        {/* Tab 1: Live Investigation Main Layout */}
        {activeTab === 'investigation' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="lg:col-span-5">
              <AlertStream
                attackScenarios={ATTACK_SCENARIOS}
                activeScenario={activeScenario}
                onSelectScenario={(sc) => {
                  setActiveScenario(sc);
                  setLogs([]);
                  setIsComplete(false);
                  setFinalReport(null);
                }}
                onStartInvestigation={handleStartInvestigation}
                isInvestigating={isInvestigating}
              />
            </div>

            <div className="lg:col-span-7">
              <InvestigationCenter
                logs={logs}
                isComplete={isComplete}
                finalReport={finalReport}
                activeScenario={activeScenario}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Digital SOC Twin */}
        {activeTab === 'soc_twin' && (
          <DigitalSocTwin
            activeScenario={activeScenario}
            isInvestigating={isInvestigating}
            logs={logs}
          />
        )}

        {/* Tab 3: SOAR Containment & HITL Approval */}
        {activeTab === 'containment' && (
          <ContainmentSOAR
            activeScenario={activeScenario}
            logs={logs}
          />
        )}

        {/* Tab 4: Threat Hunter Playground */}
        {activeTab === 'playground' && (
          <ThreatHunterPlayground />
        )}

        {/* Tab 5: Memory Vault */}
        {activeTab === 'memory' && (
          <MemoryExplorer logs={logs} />
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#080d18] py-3 px-4 text-center text-xs font-mono text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>AEGIS-SOC Autonomous Engine Active</span>
        </div>
        <div>
          <span>Multi-Agent Architecture • MITRE ATT&CK • VirusTotal • AbuseIPDB • Shodan • YARA • Sigma</span>
        </div>
      </footer>

      {/* Modals */}
      <ExecutiveReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        activeScenario={activeScenario}
        logs={logs}
        finalReport={finalReport}
      />

      <BenchmarkReportModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
      />
    </div>
  );
}
