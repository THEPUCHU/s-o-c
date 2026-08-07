import React from 'react';
import { Shield, Cpu, Activity, FileText, BarChart3, Radio, Database, Zap, UserCheck } from 'lucide-react';

export default function Header({ 
  activeScenario, 
  onSelectScenario, 
  attackScenarios, 
  isInvestigating, 
  onOpenReport, 
  onOpenBenchmark,
  activeTab,
  setActiveTab,
  pendingApprovalsCount
}) {
  return (
    <header className="border-b border-cyan-500/20 bg-[#0a0f1d]/90 backdrop-blur-md sticky top-0 z-40 px-4 py-3 shadow-xl shadow-cyan-950/20">
      <div className="max-w-[1700px] mx-auto flex flex-col lg:flex-row items-center justify-between gap-4">
        
        {/* Brand & Platform Status */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 shadow-lg shadow-cyan-500/30">
            <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
              <Shield className="w-6 h-6 text-cyan-400 animate-pulse" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-200 to-indigo-400">
                AEGIS-SOC <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-cyan-400">v2.5 AUTONOMOUS</span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-2">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Autonomous Multi-Agent Cyber Defense Platform
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 bg-[#111827] p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('investigation')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'investigation' 
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Activity className="w-4 h-4" /> Live Investigation
          </button>
          
          <button
            onClick={() => setActiveTab('soc_twin')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'soc_twin' 
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm shadow-purple-500/20' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Cpu className="w-4 h-4 text-purple-400" /> Digital SOC Twin
          </button>

          <button
            onClick={() => setActiveTab('containment')}
            className={`relative flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'containment' 
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/20' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Zap className="w-4 h-4 text-amber-400" /> Containment SOAR
            {pendingApprovalsCount > 0 && (
              <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500 text-white animate-bounce">
                {pendingApprovalsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('playground')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'playground' 
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm shadow-emerald-500/20' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Radio className="w-4 h-4 text-emerald-400" /> Threat Playground
          </button>

          <button
            onClick={() => setActiveTab('memory')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'memory' 
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm shadow-sky-500/20' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Database className="w-4 h-4 text-sky-400" /> Memory Vault
          </button>
        </nav>

        {/* Action Controls & Scenario Selector */}
        <div className="flex items-center gap-3">
          {/* Attack Scenario Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono hidden xl:inline">Scenario:</span>
            <select
              value={activeScenario.id}
              onChange={(e) => {
                const found = attackScenarios.find(s => s.id === e.target.value);
                if (found) onSelectScenario(found);
              }}
              disabled={isInvestigating}
              className="bg-slate-900 text-slate-200 text-xs rounded-lg border border-slate-700 px-3 py-1.5 focus:outline-none focus:border-cyan-500 font-mono disabled:opacity-50"
            >
              {attackScenarios.map(s => (
                <option key={s.id} value={s.id}>
                  [{s.severity}] {s.title}
                </option>
              ))}
            </select>
          </div>

          {/* Executive Report Button */}
          <button
            onClick={onOpenReport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
          >
            <FileText className="w-4 h-4 text-cyan-400" /> Executive Report
          </button>

          {/* Benchmark Report Button */}
          <button
            onClick={onOpenBenchmark}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-purple-900/60 to-indigo-900/60 hover:from-purple-800 hover:to-indigo-800 text-purple-200 border border-purple-500/30 transition-all shadow-sm"
          >
            <BarChart3 className="w-4 h-4 text-purple-400" /> Hackathon Metrics
          </button>
        </div>

      </div>
    </header>
  );
}
