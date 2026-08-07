import React, { useState } from 'react';
import { Zap, ShieldCheck, AlertTriangle, UserCheck, Check, X, ShieldAlert, Sliders } from 'lucide-react';
import { ToolEcosystem } from '../services/toolEcosystem';

export default function ContainmentSOAR({ activeScenario, logs, onApproveAction }) {
  const [approvals, setApprovals] = useState({});

  const actions = activeScenario.recommendedActions || [];

  const handleApprove = async (actionId) => {
    setApprovals(prev => ({ ...prev, [actionId]: 'APPROVING' }));
    const action = actions.find(a => a.actionId === actionId);
    if (action) {
      await ToolEcosystem.executeSOARAction(action, true);
      setApprovals(prev => ({ ...prev, [actionId]: 'APPROVED' }));
      if (onApproveAction) onApproveAction(action);
    }
  };

  const handleReject = (actionId) => {
    setApprovals(prev => ({ ...prev, [actionId]: 'REJECTED' }));
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-amber-500/20 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            SOAR Containment Center & Human-in-the-Loop (HITL) Approval
          </h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
          GUARDRAIL THRESHOLD: 85% RISK
        </span>
      </div>

      {/* Playbook Containment Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {actions.map((action) => {
          const isPending = action.hitlRequired && approvals[action.actionId] !== 'APPROVED' && approvals[action.actionId] !== 'REJECTED';
          const isApproved = approvals[action.actionId] === 'APPROVED' || (!action.hitlRequired && logs.some(l => l.phase === "Autonomous Execution" || l.phase === "Complete"));
          const isRejected = approvals[action.actionId] === 'REJECTED';

          return (
            <div
              key={action.actionId}
              className={`rounded-xl p-4 border flex flex-col justify-between transition-all ${
                isApproved
                  ? 'bg-emerald-950/30 border-emerald-500/50 text-slate-200'
                  : isRejected
                  ? 'bg-slate-950 border-slate-800 text-slate-500 opacity-60'
                  : isPending
                  ? 'bg-amber-950/40 border-amber-500/70 shadow-lg shadow-amber-500/10'
                  : 'bg-slate-900/80 border-slate-800 text-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-cyan-400">{action.actionId}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                      action.riskScore > 85 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-slate-800 text-slate-300'
                    }`}>
                      Risk Score: {action.riskScore}%
                    </span>
                  </div>
                </div>

                <h3 className="font-bold text-xs text-slate-100">{action.type}</h3>
                <p className="text-[11px] font-mono text-slate-400 mt-1">Target: <strong className="text-slate-200">{action.target}</strong></p>
              </div>

              {/* Action Approval Controls */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                {isApproved ? (
                  <span className="text-xs font-mono text-emerald-400 font-bold flex items-center gap-1.5">
                    <Check className="w-4 h-4" /> Containment Executed
                  </span>
                ) : isRejected ? (
                  <span className="text-xs font-mono text-slate-500 font-bold flex items-center gap-1.5">
                    <X className="w-4 h-4 text-rose-400" /> Action Rejected by Analyst
                  </span>
                ) : isPending ? (
                  <div className="flex items-center gap-2 w-full justify-between">
                    <span className="text-[11px] font-mono text-amber-300 flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-amber-400" /> HITL Intercept
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleReject(action.actionId)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono border border-slate-700"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprove(action.actionId)}
                        className="px-3 py-1 rounded bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-bold text-xs font-mono shadow-md shadow-amber-500/20"
                      >
                        Authorize Action
                      </button>
                    </div>
                  </div>
                ) : (
                  <span className="text-xs font-mono text-cyan-400 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Autonomous Executed
                  </span>
                )}
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
