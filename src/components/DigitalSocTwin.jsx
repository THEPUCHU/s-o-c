import React from 'react';
import { Cpu, ShieldCheck, ShieldAlert, Lock, Server, Cloud, HardDrive, Terminal, Zap } from 'lucide-react';

export default function DigitalSocTwin({ activeScenario, isInvestigating, logs }) {
  // Determine asset statuses based on scenario & logs
  const isContained = logs.some(l => l.phase === "Autonomous Execution" || l.phase === "Complete");

  const nodes = [
    {
      id: "WS-EXEC-04",
      name: "Executive Workstation #04",
      type: "Endpoint",
      ip: "10.0.1.44",
      status: isContained ? "ISOLATED" : "COMPROMISED",
      icon: Terminal
    },
    {
      id: "DC-PRIMARY",
      name: "Domain Controller AD-01",
      type: "Active Directory",
      ip: "10.0.4.10",
      status: "ATTACK_TARGET",
      icon: Server
    },
    {
      id: "CORE-DB-01",
      name: "Financial ERP Database Cluster",
      type: "Database",
      ip: "10.0.4.15",
      status: isContained ? "PROTECTED" : "AT_RISK",
      icon: HardDrive
    },
    {
      id: "AWS-S3-PROD",
      name: "Cloud Customer PII Data Lake",
      type: "AWS S3 Vault",
      ip: "arn:aws:s3:::prod-vault",
      status: isContained ? "SECURED" : "EXFIL_TARGET",
      icon: Cloud
    }
  ];

  return (
    <div className="glass-panel rounded-2xl p-4 border border-purple-500/30 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-purple-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            Digital SOC Twin - Infrastructure Defense Visualizer
          </h2>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="flex items-center gap-1.5 text-purple-400">
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping"></span> Live Twin Sync
          </span>
          <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40">
            {isContained ? "DEFENSES ACTIVE" : "THREAT PRESENT"}
          </span>
        </div>
      </div>

      {/* Interactive Network Graph Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative py-4">
        {nodes.map((node) => {
          const NodeIcon = node.icon;
          const isCompromised = node.status === "COMPROMISED";
          const isIsolated = node.status === "ISOLATED" || node.status === "SECURED" || node.status === "PROTECTED";

          return (
            <div
              key={node.id}
              className={`rounded-xl p-4 border relative transition-all duration-300 flex flex-col justify-between min-h-[160px] ${
                isCompromised
                  ? 'bg-rose-950/40 border-rose-500/80 shadow-lg shadow-rose-500/20 animate-pulse'
                  : isIsolated
                  ? 'bg-emerald-950/30 border-emerald-500/50 text-emerald-200 shadow-md shadow-emerald-500/10'
                  : 'bg-slate-900/80 border-slate-800 text-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-cyan-400">
                    <NodeIcon className="w-5 h-5" />
                  </span>
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                    isCompromised
                      ? 'bg-rose-500 text-black'
                      : isIsolated
                      ? 'bg-emerald-500 text-black'
                      : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {node.status}
                  </span>
                </div>

                <h3 className="font-bold text-xs text-slate-100">{node.name}</h3>
                <p className="text-[10px] font-mono text-slate-400 mt-0.5">{node.id} ({node.ip})</p>
              </div>

              {/* Protection Barrier Status */}
              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono">
                <span className="text-slate-400">Barrier Status:</span>
                {isIsolated ? (
                  <span className="text-emerald-400 flex items-center gap-1 font-bold">
                    <Lock className="w-3 h-3" /> HARDENED
                  </span>
                ) : (
                  <span className="text-rose-400 flex items-center gap-1 font-bold">
                    <ShieldAlert className="w-3 h-3" /> EXPOSED
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-time Defense Simulation Status */}
      <div className="bg-[#0b101f] p-3 rounded-xl border border-slate-800 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-300">
          <Zap className="w-4 h-4 text-amber-400" />
          <span>Active Perimeter Firewalls: <strong>Palo Alto & AWS WAF (Enforcing Block)</strong></span>
        </div>
        <span className="text-cyan-400">Latency: &lt;15ms</span>
      </div>

    </div>
  );
}
