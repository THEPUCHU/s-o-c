import React, { useState } from 'react';
import { Radio, Search, Terminal, FileCode, CheckCircle2, Play } from 'lucide-react';
import { ToolEcosystem } from '../services/toolEcosystem';

export default function ThreatHunterPlayground() {
  const [queryInput, setQueryInput] = useState("194.26.29.112");
  const [queryType, setQueryType] = useState("ip");
  const [results, setResults] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  const [sigmaInput, setSigmaInput] = useState(`title: Detect Encoded PowerShell Download
status: experimental
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    CommandLine|contains:
      - '-enc'
      - 'IEX'
  condition: selection`);

  const handleScan = async () => {
    setIsScanning(true);
    let res = null;
    if (queryType === "ip") {
      res = await ToolEcosystem.queryVirusTotal(queryInput, "ip");
    } else if (queryType === "sigma") {
      res = await ToolEcosystem.runSigmaRules("powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQ...");
    } else if (queryType === "yara") {
      res = await ToolEcosystem.runYaraScanner(queryInput);
    }
    setResults(res);
    setIsScanning(false);
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-emerald-500/20 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-emerald-400" />
          <h2 className="text-sm font-bold tracking-wide uppercase text-slate-200">
            Threat Hunter Playground & Custom Detection Tester
          </h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          ANALYST SANDBOX MODE
        </span>
      </div>

      {/* Control Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-[#0b101f] p-3 rounded-xl border border-slate-800">
        <div>
          <label className="text-[10px] font-mono text-slate-400 block mb-1">SCAN ENGINE TYPE</label>
          <select
            value={queryType}
            onChange={(e) => setQueryType(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 font-mono"
          >
            <option value="ip">VirusTotal / AbuseIPDB Lookup</option>
            <option value="sigma">Sigma Detection Rule Tester</option>
            <option value="yara">YARA Signature Binary Scanner</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="text-[10px] font-mono text-slate-400 block mb-1">TARGET INPUT (IP / HASH / PATTERN)</label>
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono rounded-lg px-3 py-1.5 focus:outline-none focus:border-emerald-500"
            placeholder="Enter IP address, file hash, or domain..."
          />
        </div>

        <div className="flex items-end">
          <button
            onClick={handleScan}
            disabled={isScanning}
            className="w-full py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs font-mono flex items-center justify-center gap-1.5 transition-all shadow-md shadow-emerald-500/20"
          >
            {isScanning ? "Evaluating..." : <><Play className="w-3.5 h-3.5 fill-current" /> Execute Threat Scan</>}
          </button>
        </div>
      </div>

      {/* Editor / Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
        {/* Rule Editor */}
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="text-[10px] text-slate-400 flex items-center justify-between border-b border-slate-800 pb-1">
            <span className="flex items-center gap-1"><FileCode className="w-3.5 h-3.5 text-emerald-400" /> SIGMA RULE DEFINITION</span>
            <span>YAML</span>
          </div>
          <textarea
            value={sigmaInput}
            onChange={(e) => setSigmaInput(e.target.value)}
            className="w-full h-44 bg-slate-900/60 p-2 rounded text-emerald-300 font-mono text-[11px] focus:outline-none border border-slate-800 leading-relaxed resize-none"
          />
        </div>

        {/* Scan Results Output */}
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="text-[10px] text-slate-400 flex items-center justify-between border-b border-slate-800 pb-1">
            <span className="flex items-center gap-1"><Terminal className="w-3.5 h-3.5 text-cyan-400" /> DISPATCH RESULTS TELEMETRY</span>
            <span>JSON</span>
          </div>
          <pre className="w-full h-44 bg-slate-900/60 p-2 rounded text-cyan-300 font-mono text-[11px] overflow-y-auto leading-relaxed border border-slate-800">
{results ? JSON.stringify(results, null, 2) : "// Execute scan to view real-time intelligence output..."}
          </pre>
        </div>
      </div>

    </div>
  );
}
