import React from 'react';
import { SPECIALIZED_AGENTS } from '../data/mockData';
import { Cpu, Zap, Activity, CheckCircle2, Clock, AlertTriangle, Shield } from 'lucide-react';

export default function AgentTopologyGraph({ activeAgentId, currentPhase, logs }) {
  // Find Coordinator and Domain Agents
  const coordinator = SPECIALIZED_AGENTS.find(a => a.id === 'coordinator');
  const domainAgents = SPECIALIZED_AGENTS.filter(a => a.id !== 'coordinator');

  // Count agent activity
  const getAgentStatus = (agentId) => {
    if (activeAgentId === agentId) return 'ACTIVE';
    const hasLog = logs.some(l => l.agentId === agentId);
    if (hasLog) return 'COMPLETED';
    return 'IDLE';
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 relative overflow-hidden">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(#00f0ff_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none"></div>

      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            Autonomous Multi-Agent Topology & Consensus Graph
          </h2>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span> Active Pulse
          </span>
          <span className="text-slate-400">8 Agents Synchronized</span>
        </div>
      </div>

      {/* Network Graph Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative py-2">
        
        {/* Top/Center SOC Coordinator Highlight Card */}
        <div className="md:col-span-4 bg-gradient-to-r from-cyan-950/60 via-slate-900/90 to-indigo-950/60 rounded-xl p-3 border border-cyan-500/40 relative shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                {coordinator.icon}
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-cyan-300">{coordinator.name}</h3>
                  <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    MASTER ORCHESTRATOR
                  </span>
                </div>
                <p className="text-xs text-slate-400">{coordinator.description}</p>
              </div>
            </div>
            
            <div className="text-right font-mono text-xs">
              <span className="text-slate-400">Current Phase: </span>
              <span className="text-cyan-400 font-bold uppercase">{currentPhase || "STANDBY"}</span>
            </div>
          </div>
        </div>

        {/* 7 Specialized Domain Agents */}
        {domainAgents.map((agent) => {
          const status = getAgentStatus(agent.id);
          const isActive = status === 'ACTIVE';
          const isCompleted = status === 'COMPLETED';

          return (
            <div
              key={agent.id}
              className={`rounded-xl p-3 border transition-all duration-300 relative ${
                isActive
                  ? 'bg-cyan-950/40 border-cyan-400 shadow-lg shadow-cyan-500/20 scale-[1.02]'
                  : isCompleted
                  ? 'bg-slate-900/80 border-slate-700/80 text-slate-300'
                  : 'bg-slate-950/40 border-slate-800/60 text-slate-500'
              }`}
            >
              {/* Dynamic Status Indicator Pin */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{agent.icon}</span>
                  <span className="font-bold text-xs truncate max-w-[130px]" style={{ color: agent.color }}>
                    {agent.name.replace(" Agent", "")}
                  </span>
                </div>
                
                {isActive ? (
                  <span className="flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 animate-pulse">
                    <Activity className="w-3 h-3 text-cyan-400 animate-spin" /> WORKING
                  </span>
                ) : isCompleted ? (
                  <span className="flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" /> READY
                  </span>
                ) : (
                  <span className="text-[10px] font-mono text-slate-500">IDLE</span>
                )}
              </div>

              <p className="text-[11px] text-slate-400 line-clamp-2 leading-snug">
                {agent.description}
              </p>

              {/* Connected Agent Signals indicator */}
              <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>Task Queue: OK</span>
                <span className="text-cyan-400">Consensus: 98%</span>
              </div>
            </div>
          );
        })}

      </div>
    </div>
  );
}
