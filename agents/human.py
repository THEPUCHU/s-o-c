"""Human-readable SOC incident summary agent.

This module converts raw multi-agent SOC results into a short, analyst-friendly
report. It is designed to be part of the broader SOC agent orchestration.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List


class HumanReadableReportAgent:
    """Transforms technical orchestrator output into a short plain-English report."""

    def __init__(self, case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.case_id = case_id
        self.analyst = analyst

    def build_report(self, orchestrator_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a concise incident summary from the orchestrator output."""
        decision = orchestrator_result.get("decision", "monitor")
        next_step = orchestrator_result.get("recommended_next_step", "continue_monitoring_and_collect_more_evidence")
        specialists = orchestrator_result.get("specialists", {})

        summary_lines: List[str] = []
        priority = "low"

        for name, result in specialists.items():
            if not isinstance(result, dict):
                continue

            if name == "cloud_security":
                cloud_summary = result.get("cloud_security_result", {}).get("summary", {})
                severity = cloud_summary.get("severity", "low")
                classification = cloud_summary.get("classification", "low_risk")
                if severity in {"high", "critical"} or classification in {"high_risk", "critical_risk"}:
                    summary_lines.append("Cloud security posture is highly exposed or misconfigured.")
                    priority = "high"

            elif name == "compliance_analysis":
                compliance_summary = result.get("compliance_result", {}).get("summary", {})
                classification = compliance_summary.get("classification", "compliant")
                if classification == "non_compliant":
                    summary_lines.append("Compliance posture is non-compliant with the baseline framework.")
                    priority = "high"

            elif name == "log_analysis":
                log_summary = result.get("orchestrator", {}).get("log_analysis_result", {}).get("summary", {})
                risk = log_summary.get("risk_level", "low")
                suspicious = log_summary.get("suspicious_events", 0)
                if risk == "high" or suspicious > 0:
                    summary_lines.append(f"Log review found {suspicious} suspicious events with high-risk indicators.")
                    priority = "high"

            elif name == "threat_intelligence":
                ti_summary = result.get("threat_intel_result", {}).get("summary", {})
                if ti_summary.get("overall_risk") == "high":
                    summary_lines.append("Threat intelligence shows multiple malicious indicators associated with the incident.")
                    priority = "high"

            elif name == "malware_analysis":
                malware_summary = result.get("malware_agent_result", {}).get("summary", {})
                classification = malware_summary.get("classification")
                if classification == "likely_malicious":
                    summary_lines.append("Malware analysis shows likely malicious behavior and requires containment.")
                    priority = "high"

        if not summary_lines:
            summary_lines.append("No major specialist findings were triggered for this case.")
            priority = "low"

        if decision == "escalate":
            decision_text = "Escalate this incident to the incident response team immediately."
        elif decision == "governance_review":
            decision_text = "Escalate to governance and control review for policy remediation."
        else:
            decision_text = "Continue monitoring and collect more evidence before a final action." 

        final_report = {
            "agent": "human_report",
            "case_id": self.case_id,
            "analyst": self.analyst,
            "status": "completed",
            "priority": priority,
            "decision": decision,
            "next_step": next_step,
            "summary": decision_text,
            "details": summary_lines,
            "short_report": self._short_report(decision_text, summary_lines),
        }
        return final_report

    def _short_report(self, decision_text: str, details: List[str]) -> str:
        lines = [
            f"Case {self.case_id}: {decision_text}",
            "",
        ]
        for item in details[:3]:
            lines.append(f"- {item}")
        return "\n".join(lines)

    def print_report(self, orchestrator_result: Dict[str, Any]) -> None:
        payload = self.build_report(orchestrator_result)
        print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    sample = {
        "decision": "escalate",
        "recommended_next_step": "escalate_to_ir",
        "specialists": {
            "cloud_security": {
                "cloud_security_result": {"summary": {"severity": "critical", "classification": "critical_risk"}}
            },
            "log_analysis": {
                "orchestrator": {"log_analysis_result": {"summary": {"risk_level": "high", "suspicious_events": 3}}}
            },
            "threat_intelligence": {
                "threat_intel_result": {"summary": {"overall_risk": "high"}}
            },
        },
    }
    agent = HumanReadableReportAgent(case_id="SOC-900", analyst="SOC Analyst")
    print(agent._short_report("Escalate this incident to the incident response team immediately.", [
        "Cloud security posture is highly exposed or misconfigured.",
        "Threat intelligence shows multiple malicious indicators associated with the incident.",
        "Log review found 3 suspicious events with high-risk indicators.",
    ]))


if __name__ == "__main__":
    main()
