// Autonomous Memory & Knowledge Base Store (Episodic, Semantic, Cache, Self-Learning)

class MemoryStoreService {
  constructor() {
    this.episodicMemory = []; // Execution step history per incident
    this.threatIntelCache = new Map(); // Fast key-value store for IOCs
    this.incidentHistory = []; // Past resolved incidents
    this.selfLearningLogs = [
      {
        id: "SL-101",
        timestamp: "2026-08-01T14:22:00Z",
        incidentId: "ALT-2026-1102",
        feedbackType: "HUMAN_OVERRIDE_APPROVED",
        analystNotes: "SOC Coordinator accurately prioritized threat level. Added 5% confidence weight to YARA packed entropy rules.",
        confidenceDelta: "+5.0%",
        updatedRules: ["yara_entropy_weight_v2"]
      },
      {
        id: "SL-102",
        timestamp: "2026-08-04T09:15:30Z",
        incidentId: "ALT-2026-4409",
        feedbackType: "PLAYBOOK_AUTO_TUNED",
        analystNotes: "Reduced isolation delay for AWS IAM privilege escalation scenarios from 120s to 15s.",
        confidenceDelta: "+3.2%",
        updatedRules: ["aws_iam_fast_quarantine"]
      }
    ];

    // Pre-seed Semantic Knowledge Base
    this.semanticKnowledge = {
      threatActors: [
        { name: "APT29 (Cozy Bear)", origins: "Russia", focus: "Government & Enterprise Exfiltration", signatureTools: ["Cobalt Strike", "BlackCat", "Evilginx"] },
        { name: "Lazarus Group", origins: "North Korea", focus: "Financial Infrastructure & Crypto", signatureTools: ["Trojan.AppleJeus", "BLINDINGCAN"] },
        { name: "SCATTERED SPIDER", origins: "Global", focus: "Cloud IAM & Okta SSO Hijacking", signatureTools: ["SIM Swapping", "MFA Fatigue"] }
      ],
      assetTopology: [
        { id: "WS-EXEC-04", name: "Executive Workstation #4", zone: "Corporate Endpoints", criticalScore: 8 },
        { id: "10.0.4.15", name: "Core Database Cluster", zone: "PCI-DSS Sensitive Subnet", criticalScore: 10 },
        { id: "JENKINS-BUILD-01", name: "Production CI/CD Master", zone: "DevOps Infrastructure", criticalScore: 9 }
      ]
    };
  }

  // Add item to Episodic Memory
  logEpisodicEvent(incidentId, agentId, phase, detail, data = {}) {
    const entry = {
      id: `EP-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      timestamp: new Date().toISOString(),
      incidentId,
      agentId,
      phase,
      detail,
      data
    };
    this.episodicMemory.unshift(entry);
    return entry;
  }

  // Get Episodic Memory for an Incident
  getEpisodicMemory(incidentId) {
    return this.episodicMemory.filter(e => e.incidentId === incidentId);
  }

  // Cache Threat Intel
  cacheIOC(ioc, data) {
    this.threatIntelCache.set(ioc, {
      timestamp: Date.now(),
      data
    });
  }

  // Lookup Threat Intel Cache
  getCachedIOC(ioc) {
    const item = this.threatIntelCache.get(ioc);
    if (!item) return null;
    // Cache valid for 1 hour
    if (Date.now() - item.timestamp > 3600000) {
      this.threatIntelCache.delete(ioc);
      return null;
    }
    return item.data;
  }

  // Log Self-Learning Feedback Loop
  addFeedback(incidentId, analystNotes, feedbackType = "ANALYST_APPROVED") {
    const log = {
      id: `SL-${Date.now()}`,
      timestamp: new Date().toISOString(),
      incidentId,
      feedbackType,
      analystNotes,
      confidenceDelta: "+4.5%",
      updatedRules: ["autonomous_reasoning_weight_tuned"]
    };
    this.selfLearningLogs.unshift(log);
    return log;
  }

  // Archive Resolved Incident
  archiveIncident(incident) {
    this.incidentHistory.unshift({
      ...incident,
      resolvedAt: new Date().toISOString()
    });
  }
}

export const memoryStore = new MemoryStoreService();
