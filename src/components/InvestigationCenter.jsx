import React, { useState } from 'react';
import { MITRE_ATTACK_MATRIX, SPECIALIZED_AGENTS } from '../data/mockData';
import { Activity, ShieldCheck, Terminal, GitMerge, Grid, FileCode, CheckCircle2, Clock, AlertTriangle, ChevronRight, Eye } from 'lucide-react';

export default function InvestigationCenter({ logs, isComplete, finalReport, activeScenario }) {
  const [subTab, setSubTab] = useState('stream'); // 'stream', 'reasoning', 'mitre', 'tool_logs', 'evidence'
  const [selectedLog, setSelectedLog] = useState(null);

  const getAgentObj = (agentId) => SPECIALIZED_AGENTS.find(a => a.id === agentId) || SPECIALIZED_AGENTS[0];

  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 flex flex-col gap-4">
      
      {/* Tab Selector Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-1 bg-[#0d1322] p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setSubTab('stream')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              subTab === 'stream' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-cyan-400" /> Execution Stream ({logs.length})
          </button>

          <button
            onClick={() => setSubTab('reasoning')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              subTab === 'reasoning' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitMerge className="w-3.5 h-3.5 text-purple-400" /> Reasoning Tree
          </button>

          <button
            onClick={() => setSubTab('mitre')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              subTab === 'mitre' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Grid className="w-3.5 h-3.5 text-amber-400" /> MITRE ATT&CK Matrix
          </button>

          <button
            onClick={() => setSubTab('tool_logs')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              subTab === 'tool_logs' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-emerald-400" /> Tool Execution Traces
          </button>
        </div>

        {/* Status Badge */}
        {isComplete ? (
          <span className="flex items-center gap-1.5 text-xs font-mono px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Autonomous Investigation Complete
          </span>
        ) : logs.length > 0 ? (
          <span className="flex items-center gap-1.5 text-xs font-mono px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 animate-pulse">
            <Clock className="w-3.5 h-3.5 animate-spin" /> Agents Interacting...
          </span>
        ) : (
          <span className="text-xs font-mono text-slate-500">Awaiting Dispatch Signal</span>
        )}
      </div>

      {/* SUB TAB 1: EXECUTION STREAM */}
      {subTab === 'stream' && (
        <div className="flex flex-col gap-3 max-h-[520px] overflow-y-auto pr-1">
          {logs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs flex flex-col items-center gap-2">
              <Activity className="w-8 h-8 opacity-30 text-cyan-400" />
              <p>No agent activity logged yet. Click "Dispatch Autonomous Agents" to begin.</p>
            </div>
          ) : (
            logs.map((log) => {
              const agent = getAgentObj(log.agentId);
              return (
                <div
                  key={log.id}
                  className="bg-slate-900/80 rounded-xl p-3 border border-slate-800 hover:border-slate-700 transition-all flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-base p-1.5 rounded-lg bg-slate-800 border border-slate-700">
                        {agent.icon}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-slate-200">{agent.name}</span>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
                            {log.phase}
                          </span>
                        </div>
                        <h4 className="font-bold text-xs text-cyan-300 mt-0.5">{log.title}</h4>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">{log.timestamp}</span>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed font-mono">
                    {log.detail}
                  </p>

                  {/* Tool Output / Subtasks expander preview */}
                  {log.toolOutput && (
                    <div className="flex items-center justify-between text-[11px] font-mono bg-cyan-950/30 px-3 py-1.5 rounded-lg border border-cyan-500/20 text-cyan-300">
                      <span>Tool Execution Payload Available</span>
                      <button
                        onClick={() => { setSelectedLog(log); setSubTab('tool_logs'); }}
                        className="text-cyan-400 hover:underline flex items-center gap-1"
                      >
                        Inspect Raw Output <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* SUB TAB 2: REASONING TREE */}
      {subTab === 'reasoning' && (
        <div className="bg-[#0a0f1d] p-4 rounded-xl border border-slate-800 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase font-mono">
              Task Decomposition & Multi-Agent Reasoning Graph
            </h3>
            <span className="text-xs text-purple-400 font-mono">Consensus Confidence: 98.4%</span>
          </div>

          <div className="flex flex-col gap-3 font-mono text-xs">
            {/* Root Node */}
            <div className="p-3 rounded-xl bg-purple-950/40 border border-purple-500/40 text-purple-200 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-cyan-300">Root Directive [SOC Coordinator]</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">Task Ingested</span>
              </div>
              <p className="text-slate-300">Ingest alert {activeScenario.initialAlert.alertId} and execute parallel threat investigation.</p>
            </div>

            {/* Sub Branches */}
            <div className="pl-6 border-l-2 border-purple-500/30 flex flex-col gap-3">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <span className="text-cyan-400 font-bold">Branch 1 (Threat Intel):</span> Query VirusTotal, AbuseIPDB, Shodan feeds for IP {activeScenario.initialAlert.srcIp}
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <span className="text-purple-400 font-bold">Branch 2 (Log Analysis):</span> Execute Sigma Rule matcher against SIEM telemetry
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <span className="text-rose-400 font-bold">Branch 3 (Malware Analysis):</span> YARA signature scanner & payload entropy check
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <span className="text-amber-400 font-bold">Branch 4 (Incident Response):</span> Formulate SOAR containment & HITL authorization queue
              </div>
            </div>

            {/* Consensus Decision */}
            <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300">
              <span className="font-bold text-emerald-400">Consensus Synthesis:</span> Multi-agent voting confirmed CRITICAL threat severity with zero agent conflict.
            </div>
          </div>
        </div>
      )}

      {/* SUB TAB 3: MITRE ATT&CK MATRIX */}
      {subTab === 'mitre' && (
        <div className="flex flex-col gap-3">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Highlighted tactics & techniques detected during autonomous agent analysis:</span>
            <span className="font-mono text-cyan-400">5 Techniques Identified</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-2">
            {MITRE_ATTACK_MATRIX.map((tactic) => (
              <div key={tactic.id} className="bg-slate-900/80 rounded-xl p-3 border border-slate-800 flex flex-col gap-2">
                <div className="border-b border-slate-800 pb-1 flex items-center justify-between">
                  <span className="font-bold text-xs text-cyan-300">{tactic.tactic}</span>
                  <span className="font-mono text-[10px] text-slate-500">{tactic.id}</span>
                </div>

                <div className="flex flex-col gap-1.5">
                  {tactic.techniques.map((tech) => {
                    const isDetected = activeScenario.mitreTechniques.some(m => m.startsWith(tech.id));
                    return (
                      <div
                        key={tech.id}
                        className={`p-2 rounded-lg text-xs font-mono flex items-center justify-between border ${
                          isDetected
                            ? 'bg-rose-950/50 border-rose-500/60 text-rose-200 font-bold shadow-sm shadow-rose-500/20'
                            : 'bg-slate-950/40 border-slate-800 text-slate-500 opacity-60'
                        }`}
                      >
                        <div className="truncate">
                          <div>{tech.name}</div>
                          <div className="text-[10px] text-slate-400">{tech.id}</div>
                        </div>
                        {isDetected && (
                          <span className="px-1.5 py-0.5 text-[9px] rounded bg-rose-500 text-black font-bold">
                            DETECTED
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB TAB 4: TOOL EXECUTION LOGS */}
      {subTab === 'tool_logs' && (
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono text-xs text-emerald-400 max-h-[480px] overflow-y-auto">
          <div className="text-[11px] text-slate-400 border-b border-slate-800 pb-2 mb-3 flex items-center justify-between">
            <span>RAW TOOL EXECUTION TELEMETRY & API RESPONSES</span>
            <span>FORMAT: JSON / RAW</span>
          </div>

          <pre className="whitespace-pre-wrap leading-relaxed">
{JSON.stringify(
  logs.filter(l => l.toolOutput).map(l => ({
    timestamp: l.timestamp,
    agent: l.agentId,
    toolOutput: l.toolOutput
  })),
  null,
  2
) || "// No tool execution logs available yet. Run investigation."}
          </pre>
        </div>
      )}

    </div>
  );
}
