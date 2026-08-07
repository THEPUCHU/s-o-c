// Multi-Agent SOC Execution Engine & Orchestrator

import { ToolEcosystem } from './toolEcosystem';
import { memoryStore } from './memoryStore';
import { COMPLIANCE_FRAMEWORKS } from '../data/mockData';

export class AgentOrchestrator {
  constructor(onStepCallback) {
    this.onStep = onStepCallback || (() => {});
    this.isInvestigating = false;
  }

  // Execute full autonomous multi-agent threat investigation pipeline
  async runInvestigation(scenario) {
    this.isInvestigating = true;
    const incidentId = scenario.initialAlert.alertId;
    const logs = [];
    const executionTrace = [];
    const evidenceList = [];
    let overallConfidence = 94.5;

    const emitStep = (agentId, phase, title, detail, status = "active", extra = {}) => {
      const stepData = {
        id: `STEP-${Date.now()}-${Math.floor(Math.random()*1000)}`,
        timestamp: new Date().toLocaleTimeString(),
        incidentId,
        agentId,
        phase,
        title,
        detail,
        status,
        ...extra
      };
      logs.push(stepData);
      memoryStore.logEpisodicEvent(incidentId, agentId, phase, detail, stepData);
      this.onStep({ logs: [...logs], currentStep: stepData, isComplete: false });
    };

    // --- PHASE 1: SOC Coordinator Alert Ingestion & Task Decomposition ---
    emitStep("coordinator", "Ingestion", "Alert Ingestion & Plan Decomposition", 
      `Received alert ${incidentId} [${scenario.severity}]. Decomposing into parallel domain investigation tasks...`, "active");
    await new Promise(r => setTimeout(r, 600));

    const subTasks = [
      { id: "TASK-1", agent: "threat_intel", name: "Perform IOC Reputation Lookup & WHOIS Enrichment" },
      { id: "TASK-2", agent: "log_analysis", name: "Parse SIEM Event Logs & Match Sigma Detection Rules" },
      { id: "TASK-3", agent: "malware_analysis", name: "Perform Static Payload Evaluation & YARA Signature Scan" },
      { id: "TASK-4", agent: "cloud_security", name: "Audit Cloud Telemetry & IAM Role Manipulations" }
    ];

    emitStep("coordinator", "Planning", "Agent Task Assignment", 
      `Dispatched 4 parallel sub-tasks across Threat Intel, Log Analysis, Malware Analysis, and Cloud Security agents.`, "completed", { subTasks });
    await new Promise(r => setTimeout(r, 700));

    // --- PHASE 2: Parallel Domain Agent Execution & Tool Interaction ---
    emitStep("threat_intel", "Enrichment", "Querying External Threat Feeds", 
      `Interacting with VirusTotal, AbuseIPDB, Shodan & MISP for IP ${scenario.initialAlert.srcIp || "IOCs"}...`, "active");
    
    // Execute Threat Intel queries
    const vtResults = await ToolEcosystem.queryVirusTotal(scenario.initialAlert.srcIp || scenario.iocs.ips[0] || "194.26.29.112", "ip");
    const abuseResults = await ToolEcosystem.queryAbuseIPDB(scenario.initialAlert.srcIp || "194.26.29.112");
    const shodanResults = await ToolEcosystem.queryShodan(scenario.initialAlert.srcIp || "194.26.29.112");

    evidenceList.push({ tool: "VirusTotal", verdict: vtResults.threatVerdict, score: `${vtResults.positives}/${vtResults.totalEngines}` });
    evidenceList.push({ tool: "AbuseIPDB", verdict: `Abuse Score ${abuseResults.abuseConfidenceScore}%`, reports: abuseResults.totalReports });

    emitStep("threat_intel", "Enrichment", "Enrichment Complete", 
      `VirusTotal Verdict: ${vtResults.threatVerdict} (${vtResults.positives}/${vtResults.totalEngines} engines). AbuseIPDB Confidence: ${abuseResults.abuseConfidenceScore}%.`, "completed", { toolOutput: [vtResults, abuseResults, shodanResults] });
    await new Promise(r => setTimeout(r, 600));

    // Execute Log Analysis
    emitStep("log_analysis", "Log Parsing", "Correlating SIEM Telemetry", 
      `Parsing raw security logs and matching 1,240 Sigma detection rules...`, "active");
    const sigmaResults = await ToolEcosystem.runSigmaRules(scenario.initialAlert.rawLog);
    
    emitStep("log_analysis", "Log Parsing", "Sigma Pattern Match Detected", 
      `Matched ${sigmaResults.matchedRulesCount} critical Sigma rules: ${sigmaResults.matches.map(m=>m.ruleTitle).join(", ")}.`, "completed", { toolOutput: [sigmaResults] });
    await new Promise(r => setTimeout(r, 600));

    // Execute Malware Analysis
    emitStep("malware_analysis", "Binary Inspection", "Running YARA Scanner & Entropy Calculation", 
      `Evaluating payload hash against YARA rule database...`, "active");
    const yaraResults = await ToolEcosystem.runYaraScanner(scenario.iocs.hashes[0] || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");

    emitStep("malware_analysis", "Binary Inspection", "YARA Signature Matched", 
      `Matched rule: '${yaraResults.matches[0]?.ruleName}'. Entropy: 7.92 (High packing / encryption detected).`, "completed", { toolOutput: [yaraResults] });
    await new Promise(r => setTimeout(r, 600));

    // Execute Cloud Security Audit
    emitStep("cloud_security", "Cloud Audit", "Inspecting IAM Telemetry & S3 Buckets", 
      `Auditing CloudTrail logs for unauthorized administrative privilege escalation...`, "completed", { cloudStatus: "Privilege Escalation Detected on IAM Service Role" });
    await new Promise(r => setTimeout(r, 500));

    // --- PHASE 3: Consensus, Root Cause Analysis & MITRE Mapping ---
    emitStep("coordinator", "Consensus", "Multi-Agent Consensus & Root Cause Analysis", 
      `Synthesizing evidence across 5 agents. Threat Confidence Score: ${overallConfidence}%. Primary Vector: Spearphishing -> Process Injection -> Ransomware Exfiltration.`, "active");
    await new Promise(r => setTimeout(r, 800));

    // --- PHASE 4: Compliance Assessment ---
    const regulatoryHits = COMPLIANCE_FRAMEWORKS.slice(0, 3);
    emitStep("compliance", "Compliance Audit", "Evaluating Regulatory Impact", 
      `Identified potential breaches under ${regulatoryHits.map(r=>r.name).join(", ")}. Breach notification required within 72h under GDPR Art. 33.`, "completed", { regulatoryHits });
    await new Promise(r => setTimeout(r, 600));

    // --- PHASE 5: Incident Response & SOAR Playbook Generation ---
    emitStep("incident_response", "SOAR Playbook", "Formulating Containment Actions", 
      `Generated 4 containment directives. Evaluating risk scores against HITL governance rules...`, "active");
    await new Promise(r => setTimeout(r, 700));

    // Evaluate actions with SOAR tool
    const actionResults = [];
    for (const act of scenario.recommendedActions) {
      const res = await ToolEcosystem.executeSOARAction(act, false);
      actionResults.push(res);
      
      if (res.status === "PENDING_HUMAN_APPROVAL") {
        emitStep("human_approval", "HITL Intercept", `High-Risk Action Blocked (${act.riskScore}% Risk)`, 
          res.message, "pending_approval", { action: act, res });
      } else {
        emitStep("incident_response", "Autonomous Execution", `Executed Action: ${act.type}`, 
          res.message, "completed", { action: act, res });
      }
      await new Promise(r => setTimeout(r, 300));
    }

    // --- PHASE 6: Investigation Summary & Final Consensus ---
    this.isInvestigating = false;
    const finalReport = {
      incidentId,
      severity: scenario.severity,
      confidenceScore: overallConfidence,
      rootCause: `Attack Vector: ${scenario.category}. Initial Compromise via ${scenario.initialAlert.host} by user ${scenario.initialAlert.user}. Encrypted C2 communications established to ${scenario.iocs.ips.join(", ")}.`,
      mitreMapping: scenario.mitreTechniques,
      evidenceSummary: evidenceList,
      actionResults,
      logs
    };

    this.onStep({
      logs: [...logs],
      currentStep: {
        id: "STEP-FINAL",
        timestamp: new Date().toLocaleTimeString(),
        agentId: "coordinator",
        phase: "Complete",
        title: "Autonomous Investigation Complete",
        detail: "Full incident lifecycle investigated, correlated, and documented. Executive report available.",
        status: "completed"
      },
      isComplete: true,
      finalReport
    });

    return finalReport;
  }
}
