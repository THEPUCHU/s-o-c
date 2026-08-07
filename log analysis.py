"""SOC-focused log analysis agent.

This module acts as a specialist log-analysis agent inside a larger SOC.
It reads log lines, detects suspicious patterns, correlates them into findings,
and returns structured security triage output for a higher-level orchestrator.

Usage:
    python "log analysis.py" --json logs.json --case-id INC-1001 --analyst "SOC Analyst"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List


class LogAnalysisAgent:
    """Specialist agent for SOC log triage and anomaly detection."""

    def __init__(self, case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.case_id = case_id
        self.analyst = analyst
        self.last_report: Dict[str, Any] = {}

    def analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        parsed = []

        for line in logs:
            entry = self._parse_line(line)
            if entry:
                parsed.append(entry)
                if self._is_suspicious(entry):
                    findings.append(self._build_finding(entry))

        summary = self._summarize(findings, parsed)
        report = {
            "agent": "log_analysis",
            "case_id": self.case_id,
            "analyst": self.analyst,
            "status": "completed",
            "summary": summary,
            "findings": findings,
            "events": parsed[:50],
            "recommended_actions": self._recommended_actions(findings),
        }
        self.last_report = report
        return report

    def _parse_line(self, line: str) -> Dict[str, Any]:
        entry: Dict[str, Any] = {"raw": line}
        patterns = {
            "timestamp": r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})?)",
            "ip": r"(?:\b\d{1,3}(?:\.\d{1,3}){3}\b)",
            "user": r"(?:user(?:name)?|account|principal)[=:\s]+([A-Za-z0-9_.-]+)",
            "source": r"(?:src|source|host|hostname)[=:\s]+([A-Za-z0-9_.-]+)",
            "event": r"(?:EVENT|event|action|message)[=:\s]+([^|\n]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                entry[key] = match.group(1) if key not in {"timestamp", "ip"} else match.group(0)

        entry["normalized"] = line.lower()
        return entry

    def _is_suspicious(self, entry: Dict[str, Any]) -> bool:
        suspicious_terms = [
            "failed login",
            "login failed",
            "admin",
            "powershell",
            "cmd.exe",
            "rundll32",
            "malware",
            "suspicious",
            "denied",
            "unauthorized",
            "remote desktop",
            "execution",
            "download",
            "webshell",
            "credential",
            "new user",
            "privilege",
            "lsass",
            "schtasks",
            "regsvr32",
        ]
        normalized = entry.get("normalized", "")
        return any(term in normalized for term in suspicious_terms)

    def _build_finding(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        message = entry.get("event") or entry.get("raw", "")
        return {
            "category": "log_anomaly",
            "severity": self._severity_for_message(entry.get("normalized", "")),
            "title": "Suspicious log activity detected",
            "details": message[:300],
            "evidence": entry,
        }

    def _severity_for_message(self, message: str) -> str:
        high_terms = ["powershell", "rundll32", "malware", "webshell", "privilege", "lsass", "credential"]
        medium_terms = ["failed login", "denied", "unauthorized", "download", "remote desktop", "admin", "login failed"]
        if any(t in message for t in high_terms):
            return "high"
        if any(t in message for t in medium_terms):
            return "medium"
        return "low"

    def _summarize(self, findings: List[Dict[str, Any]], parsed: List[Dict[str, Any]]) -> Dict[str, Any]:
        severity_order = {"low": 1, "medium": 2, "high": 3}
        top = max((f.get("severity", "low") for f in findings), default="low", key=lambda x: severity_order.get(x, 1))
        return {
            "total_events": len(parsed),
            "suspicious_events": len(findings),
            "highest_severity": top,
            "risk_level": self._risk_level(top, len(findings)),
        }

    def _risk_level(self, severity: str, count: int) -> str:
        if severity == "high" or count >= 5:
            return "high"
        if severity == "medium" or count >= 2:
            return "medium"
        return "low"

    def _recommended_actions(self, findings: List[Dict[str, Any]]) -> List[str]:
        if not findings:
            return ["Continue normal monitoring and alert tuning"]
        actions = [
            "Review affected hosts and user accounts",
            "Correlate events across endpoint and network telemetry",
            "Check for privilege escalation or lateral movement",
        ]
        if any(f.get("severity") == "high" for f in findings):
            actions.append("Escalate to IR and preserve relevant logs for forensic review")
        return actions

    def print_report(self, pretty: bool = True) -> None:
        payload = json.dumps(self.last_report, indent=2 if pretty else None, sort_keys=True)
        print(payload)


class SOCAgentOrchestrator:
    """Coordination layer for a log-analysis specialist inside a SOC workflow."""

    def __init__(self, case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.case_id = case_id
        self.analyst = analyst
        self.log_agent = LogAnalysisAgent(case_id=case_id, analyst=analyst)

    def analyze_case_logs(self, logs: List[str]) -> Dict[str, Any]:
        result = self.log_agent.analyze_logs(logs)
        return {
            "agent": "soc_orchestrator",
            "case_id": self.case_id,
            "log_analysis_result": result,
            "next_step": "escalate_to_ir" if result["summary"]["risk_level"] == "high" else "monitor_and_review",
            "orchestration_plan": {
                "primary_agent": "log_analysis",
                "secondary_agents": ["threat_intelligence", "malware_analysis", "identity_security"],
                "decision": "escalate" if result["summary"]["risk_level"] == "high" else "review",
            },
        }


class SOCLogWorkflow:
    """Example workflow demonstrating log analysis as part of a multi-agent SOC."""

    def __init__(self, case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.orchestrator = SOCAgentOrchestrator(case_id=case_id, analyst=analyst)

    def run(self, logs: List[str]) -> Dict[str, Any]:
        return {
            "workflow": "soc_log_analysis_pipeline",
            "orchestrator": self.orchestrator.analyze_case_logs(logs),
            "status": "agentic_log_analysis_complete",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="SOC log analysis agent")
    parser.add_argument("--json", help="Path to a JSON file containing log entries")
    parser.add_argument("--case-id", default="CASE-UNKNOWN", help="SOC case identifier")
    parser.add_argument("--analyst", default="SOC Analyst", help="Analyst or team name")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON output")
    args = parser.parse_args()

    if not args.json:
        print("[ERROR] Please provide a JSON file using --json", file=sys.stderr)
        return 1

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as exc:
        print(f"[ERROR] Could not read log JSON: {exc}", file=sys.stderr)
        return 2

    logs = payload.get("logs", payload if isinstance(payload, list) else [])
    if not isinstance(logs, list):
        print("[ERROR] JSON must contain a list of logs or an object with a 'logs' list.", file=sys.stderr)
        return 3

    try:
        workflow = SOCLogWorkflow(case_id=args.case_id, analyst=args.analyst)
        result = workflow.run(logs)
        if args.compact:
            print(json.dumps(result, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Analysis failed: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
