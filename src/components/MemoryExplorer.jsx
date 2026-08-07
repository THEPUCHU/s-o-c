import React, { useState } from 'react';
import { Database, Clock, Brain, Cpu, MessageSquare, ThumbsUp } from 'lucide-react';
import { memoryStore } from '../services/memoryStore';

export default function MemoryExplorer({ logs }) {
  const [memTab, setMemTab] = useState('episodic'); // 'episodic', 'semantic', 'self_learning'
  const [feedbackInput, setFeedbackInput] = useState('');
  const [feedbackList, setFeedbackList] = useState(memoryStore.selfLearningLogs);

  const handleAddFeedback = () => {
    if (!feedbackInput.trim()) return;
    const item = memoryStore.addFeedback('ALT-2026-8891', feedbackInput);
    setFeedbackList([...memoryStore.selfLearningLogs]);
    setFeedbackInput('');
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-sky-500/20 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            Autonomous Memory Vault & Self-Learning Knowledge Base
          </h2>
        </div>
        <div className="flex items-center gap-1 bg-[#0d1322] p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setMemTab('episodic')}
            className={`px-3 py-1 rounded-lg font-mono font-semibold transition-all ${
              memTab === 'episodic' ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40' : 'text-slate-400'
            }`}
          >
            Episodic ({logs.length})
          </button>
          <button
            onClick={() => setMemTab('semantic')}
            className={`px-3 py-1 rounded-lg font-mono font-semibold transition-all ${
              memTab === 'semantic' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' : 'text-slate-400'
            }`}
          >
            Semantic Graph
          </button>
          <button
            onClick={() => setMemTab('self_learning')}
            className={`px-3 py-1 rounded-lg font-mono font-semibold transition-all ${
              memTab === 'self_learning' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400'
            }`}
          >
            Self-Learning Feedback ({feedbackList.length})
          </button>
        </div>
      </div>

      {/* EPISODIC MEMORY */}
      {memTab === 'episodic' && (
        <div className="flex flex-col gap-2 max-h-[460px] overflow-y-auto font-mono text-xs">
          {logs.map((log) => (
            <div key={log.id} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sky-400 font-bold">[{log.agentId}]</span>
                <span className="text-slate-200">{log.title}</span>
              </div>
              <span className="text-slate-500 text-[10px]">{log.timestamp}</span>
            </div>
          ))}
        </div>
      )}

      {/* SEMANTIC GRAPH */}
      {memTab === 'semantic' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex flex-col gap-2">
            <h3 className="font-bold text-purple-300 font-mono border-b border-slate-800 pb-1">Known Threat Actor Profiling</h3>
            {memoryStore.semanticKnowledge.threatActors.map(ta => (
              <div key={ta.name} className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <div className="font-bold text-slate-100">{ta.name} ({ta.origins})</div>
                <div className="text-[11px] text-slate-400">Focus: {ta.focus}</div>
                <div className="text-[10px] font-mono text-purple-400 mt-1">Signature Tools: {ta.signatureTools.join(", ")}</div>
              </div>
            ))}
          </div>

          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex flex-col gap-2">
            <h3 className="font-bold text-cyan-300 font-mono border-b border-slate-800 pb-1">Organizational Asset Topology</h3>
            {memoryStore.semanticKnowledge.assetTopology.map(asset => (
              <div key={asset.id} className="bg-slate-950 p-2 rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-100">{asset.name}</div>
                  <div className="text-[10px] text-slate-500">{asset.id} • {asset.zone}</div>
                </div>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                  Criticality: {asset.criticalScore}/10
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SELF-LEARNING FEEDBACK */}
      {memTab === 'self_learning' && (
        <div className="flex flex-col gap-3 text-xs">
          {/* Feedback Form */}
          <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800 flex items-center gap-2">
            <input
              type="text"
              value={feedbackInput}
              onChange={(e) => setFeedbackInput(e.target.value)}
              placeholder="Enter analyst feedback to tune agent reasoning weights..."
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 font-mono text-xs focus:outline-none focus:border-emerald-500"
            />
            <button
              onClick={handleAddFeedback}
              className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold font-mono text-xs flex items-center gap-1 shadow-md shadow-emerald-500/20"
            >
              <ThumbsUp className="w-3.5 h-3.5" /> Submit Feedback
            </button>
          </div>

          {/* Feedback Logs */}
          <div className="flex flex-col gap-2 max-h-[380px] overflow-y-auto">
            {feedbackList.map(item => (
              <div key={item.id} className="bg-slate-900/70 p-3 rounded-xl border border-slate-800 font-mono">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-emerald-400 font-bold">{item.feedbackType}</span>
                  <span className="text-slate-500 text-[10px]">{item.timestamp}</span>
                </div>
                <p className="text-slate-300 text-[11px] mb-2">{item.analystNotes}</p>
                <div className="flex items-center gap-3 text-[10px] text-slate-400">
                  <span>Confidence Delta: <strong className="text-emerald-400">{item.confidenceDelta}</strong></span>
                  <span>Tuned Rules: {item.updatedRules.join(", ")}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
