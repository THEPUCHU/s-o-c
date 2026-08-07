import React from 'react';
import { AlertOctagon, Play, ShieldAlert, Terminal, Server, User, Globe, ArrowRight } from 'lucide-react';

export default function AlertStream({ 
  attackScenarios, 
  activeScenario, 
  onSelectScenario, 
  onStartInvestigation, 
  isInvestigating 
}) {
  const alert = activeScenario.initialAlert;

  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 flex flex-col gap-4">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-rose-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            SIEM Alert Stream & Attack Scenario Simulator
          </h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
          LIVE FEED: {alert.alertId}
        </span>
      </div>

      {/* Attack Scenario Trigger Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {attackScenarios.map((sc) => {
          const isSelected = sc.id === activeScenario.id;
          return (
            <button
              key={sc.id}
              onClick={() => onSelectScenario(sc)}
              disabled={isInvestigating}
              className={`text-left p-3 rounded-xl border transition-all text-xs relative ${
                isSelected
                  ? 'bg-gradient-to-r from-cyan-950/70 to-indigo-950/70 border-cyan-400 text-slate-100 shadow-md shadow-cyan-500/10'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono font-bold text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300">
                  {sc.category}
                </span>
                <span className={`font-mono text-[10px] font-bold ${
                  sc.severity === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'
                }`}>
                  {sc.severity}
                </span>
              </div>
              <h4 className="font-bold text-slate-200 truncate">{sc.title}</h4>
              <p className="text-[11px] text-slate-400 line-clamp-1 mt-1">{sc.summary}</p>
            </button>
          );
        })}
      </div>

      {/* Active Ingested Alert Details Box */}
      <div className="bg-[#0b101d] rounded-xl p-4 border border-slate-800 flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span className="font-bold text-xs text-slate-200">{activeScenario.title}</span>
          </div>
          <span className="text-[11px] font-mono text-slate-400">{alert.timestamp}</span>
        </div>

        {/* Telemetry Chips */}
        <div className="grid grid-cols-3 gap-2 text-xs font-mono">
          <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-[10px] text-slate-500">TARGET HOST</div>
              <div className="text-slate-200 font-bold truncate">{alert.host}</div>
            </div>
          </div>

          <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 flex items-center gap-2">
            <User className="w-4 h-4 text-indigo-400" />
            <div>
              <div className="text-[10px] text-slate-500">USER IDENTITY</div>
              <div className="text-slate-200 font-bold truncate">{alert.user}</div>
            </div>
          </div>

          <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 flex items-center gap-2">
            <Globe className="w-4 h-4 text-amber-400" />
            <div>
              <div className="text-[10px] text-slate-500">SOURCE IP</div>
              <div className="text-slate-200 font-bold truncate">{alert.srcIp}</div>
            </div>
          </div>
        </div>

        {/* Raw Log Telemetry Box */}
        <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 font-mono text-[11px] text-emerald-400 flex flex-col gap-1">
          <div className="text-[10px] text-slate-500 flex items-center gap-1">
            <Terminal className="w-3 h-3 text-slate-400" /> RAW SIEM TELEMETRY STREAM
          </div>
          <div className="truncate text-emerald-400/90">{alert.rawLog}</div>
        </div>

        {/* Trigger Investigation Button */}
        <button
          onClick={onStartInvestigation}
          disabled={isInvestigating}
          className={`w-full py-3 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-lg ${
            isInvestigating
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-black font-extrabold shadow-cyan-500/25'
          }`}
        >
          {isInvestigating ? (
            <>
              <span className="w-4 h-4 rounded-full border-2 border-slate-400 border-t-transparent animate-spin"></span>
              Autonomous Multi-Agent Investigation in Progress...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" /> Dispatch Autonomous Agents
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

    </div>
  );
}
