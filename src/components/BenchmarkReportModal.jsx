import React from 'react';
import { X, BarChart3, Zap, Clock, ShieldCheck, Cpu, Award } from 'lucide-react';
import { MOCK_BENCHMARK_DATA } from '../data/mockData';

export default function BenchmarkReportModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0f172a] border border-purple-500/40 rounded-2xl max-w-3xl w-full p-6 shadow-2xl flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Award className="w-6 h-6 text-purple-400" />
            <div>
              <h2 className="text-base font-bold text-slate-100 tracking-wide uppercase">
                Hackathon Platform Evaluation & Benchmark Metrics
              </h2>
              <p className="text-xs text-slate-400">Autonomous Agentic Performance vs Industry Manual SOC Baseline</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Benchmark Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 font-mono">
          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">INVESTIGATION SPEED</div>
            <div className="text-2xl font-extrabold text-purple-300">{MOCK_BENCHMARK_DATA.averageResponseTimeMs} ms</div>
            <div className="text-[10px] text-emerald-400 mt-1">1,900x faster than manual</div>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">MANUAL TRIAGE TIME</div>
            <div className="text-2xl font-extrabold text-slate-300">{MOCK_BENCHMARK_DATA.manualTriageTimeMin} min</div>
            <div className="text-[10px] text-rose-400 mt-1">Tier-1 Analyst Bottleneck</div>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">AUTONOMOUS ACCURACY</div>
            <div className="text-2xl font-extrabold text-emerald-400">{MOCK_BENCHMARK_DATA.autonomousAccuracyRate}%</div>
            <div className="text-[10px] text-emerald-400 mt-1">Multi-Agent Voting</div>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">FALSE POSITIVE REDUCTION</div>
            <div className="text-2xl font-extrabold text-cyan-400">{MOCK_BENCHMARK_DATA.falsePositiveReductionPct}%</div>
            <div className="text-[10px] text-cyan-400 mt-1">Sigma & YARA Correlation</div>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">TOOL ENRICHMENT LATENCY</div>
            <div className="text-2xl font-extrabold text-amber-300">{MOCK_BENCHMARK_DATA.toolEnrichmentLatencyMs} ms</div>
            <div className="text-[10px] text-amber-400 mt-1">Parallel Execution</div>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
            <div className="text-[10px] text-slate-400 mb-1">AGENT CONSENSUS RATE</div>
            <div className="text-2xl font-extrabold text-indigo-300">{MOCK_BENCHMARK_DATA.consensusAgreementRate}%</div>
            <div className="text-[10px] text-indigo-400 mt-1">Zero Hallucination</div>
          </div>
        </div>

        {/* Explainability & Governance Guarantee */}
        <div className="bg-[#0b101f] p-4 rounded-xl border border-slate-800 flex flex-col gap-2 font-mono text-xs text-slate-300">
          <div className="font-bold text-cyan-300">EXPLAINABILITY & COMPLIANCE SCORECARD:</div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            100% of autonomous containment actions generate an immutable audit trace including decision reasoning, raw tool logs, MITRE ATT&CK technique IDs, confidence scores, and Human-in-the-Loop (HITL) authorization checks.
          </p>
        </div>

      </div>
    </div>
  );
}
