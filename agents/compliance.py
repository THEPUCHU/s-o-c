"""SOC-focused compliance analysis agent.

This module acts as a specialist compliance agent for a security operations
center. It checks whether the environment is aligned with policy frameworks,
control baselines, and audit expectations, then produces structured outputs for
SOC triage and governance workflows.

Usage:
    python compliance.py --json control-data.json --case-id INC-1001 --analyst "SOC Analyst"
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List


class ComplianceAnalysisAgent:
    """Specialist agent for compliance posture assessment in a SOC environment."""

    def __init__(self, framework: str = "NIST-800-53", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.framework = framework
        self.case_id = case_id
        self.analyst = analyst
        self.last_report: Dict[str, Any] = {}

    def analyze_controls(self, controls: Dict[str, Any]) -> Dict[str, Any]:
        findings = []
        findings.extend(self._check_access_control(controls.get("access_control", {})))
        findings.extend(self._check_logging(controls.get("logging", {})))
        findings.extend(self._check_asset_management(controls.get("asset_management", {})))
        findings.extend(self._check_vulnerability_management(controls.get("vulnerability_management", {})))
        findings.extend(self._check_incident_response(controls.get("incident_response", {})))
        findings.extend(self._check_data_protection(controls.get("data_protection", {})))

        compliance_score = self._calculate_compliance_score(findings)
        severity = self._severity_from_score(compliance_score)
        confidence = self._confidence(findings)

        report = {
            "agent": "compliance_analysis",
            "case_id": self.case_id,
            "analyst": self.analyst,
            "framework": self.framework,
            "status": "completed",
            "summary": {
                "findings_count": len(findings),
                "compliance_score": compliance_score,
                "severity": severity,
                "confidence": confidence,
                "classification": self._classify(compliance_score),
            },
            "findings": findings,
            "recommended_actions": self._recommended_actions(findings),
        }
        self.last_report = report
        return report

    def _check_access_control(self, access_control: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if access_control.get("mfa_required") is False:
            findings.append({
                "category": "access_control",
                "severity": "high",
                "title": "MFA not enforced",
                "details": "Multi-factor authentication is not required for privileged users.",
                "evidence": access_control,
            })

        if access_control.get("least_privilege") is False:
            findings.append({
                "category": "access_control",
                "severity": "high",
                "title": "Least privilege not enforced",
                "details": "Users or roles have broader access than required by function.",
                "evidence": access_control,
            })

        if access_control.get("inactive_accounts"):
            findings.append({
                "category": "access_control",
                "severity": "medium",
                "title": "Dormant accounts present",
                "details": "Inactive or stale accounts remain active and should be reviewed.",
                "evidence": access_control,
            })

        return findings

    def _check_logging(self, logging: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if logging.get("centralized_logging") is False:
            findings.append({
                "category": "logging",
                "severity": "high",
                "title": "Centralized logging missing",
                "details": "Security-relevant events are not aggregated in a central monitoring platform.",
                "evidence": logging,
            })

        if logging.get("retention_days", 0) < 90:
            findings.append({
                "category": "logging",
                "severity": "medium",
                "title": "Log retention below baseline",
                "details": "Retention period is shorter than expected for audit and forensic investigation.",
                "evidence": logging,
            })

        if logging.get("privileged_event_monitoring") is False:
            findings.append({
                "category": "logging",
                "severity": "high",
                "title": "Privileged access not monitored",
                "details": "Administrative actions are not adequately tracked and alerted.",
                "evidence": logging,
            })

        return findings

    def _check_asset_management(self, asset_management: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if asset_management.get("inventory_complete") is False:
            findings.append({
                "category": "asset_management",
                "severity": "medium",
                "title": "Asset inventory incomplete",
                "details": "Not all systems and software are tracked in the approved inventory.",
                "evidence": asset_management,
            })

        if asset_management.get("owner_assigned") is False:
            findings.append({
                "category": "asset_management",
                "severity": "medium",
                "title": "Asset ownership not assigned",
                "details": "Systems do not have identifiable owners for governance and response.",
                "evidence": asset_management,
            })

        return findings

    def _check_vulnerability_management(self, vulnerability_management: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if vulnerability_management.get("patching_compliant") is False:
            findings.append({
                "category": "vulnerability_management",
                "severity": "high",
                "title": "Patch compliance gap",
                "details": "Required security patches are not being applied within the expected time window.",
                "evidence": vulnerability_management,
            })

        if vulnerability_management.get("vulnerability_scan_frequency_days", 30) > 14:
            findings.append({
                "category": "vulnerability_management",
                "severity": "medium",
                "title": "Vulnerability scans infrequent",
                "details": "Scanning frequency is slower than the policy baseline.",
                "evidence": vulnerability_management,
            })

        return findings

    def _check_incident_response(self, incident_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if incident_response.get("playbooks_defined") is False:
            findings.append({
                "category": "incident_response",
                "severity": "medium",
                "title": "Incident response playbooks missing",
                "details": "Formal procedures for containment and escalation are not defined.",
                "evidence": incident_response,
            })

        if incident_response.get("testing_exercised") is False:
            findings.append({
                "category": "incident_response",
                "severity": "medium",
                "title": "IR exercises not completed",
                "details": "The team has not validated response readiness through exercises or simulations.",
                "evidence": incident_response,
            })

        return findings

    def _check_data_protection(self, data_protection: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        if data_protection.get("encryption_at_rest") is False:
            findings.append({
                "category": "data_protection",
                "severity": "high",
                "title": "Encryption at rest not enforced",
                "details": "Sensitive data is not encrypted when stored.",
                "evidence": data_protection,
            })

        if data_protection.get("backup_verified") is False:
            findings.append({
                "category": "data_protection",
                "severity": "medium",
                "title": "Backups not validated",
                "details": "Backup recovery has not been validated against defined recovery objectives.",
                "evidence": data_protection,
            })

        return findings

    def _calculate_compliance_score(self, findings: List[Dict[str, Any]]) -> int:
        weights = {"low": 10, "medium": 20, "high": 35}
        total = 100
        for finding in findings:
            total -= weights.get(finding.get("severity", "low"), 10)
        return max(0, min(total, 100))

    def _severity_from_score(self, score: int) -> str:
        if score < 50:
            return "high"
        if score < 75:
            return "medium"
        return "low"

    def _confidence(self, findings: List[Dict[str, Any]]) -> str:
        if len(findings) >= 5:
            return "high"
        if len(findings) >= 2:
            return "medium"
        return "low"

    def _classify(self, score: int) -> str:
        if score < 50:
            return "non_compliant"
        if score < 75:
            return "partially_compliant"
        return "compliant"

    def _recommended_actions(self, findings: List[Dict[str, Any]]) -> List[str]:
        actions: List[str] = []
        categories = {f["category"] for f in findings}

        if "access_control" in categories:
            actions.append("Enforce MFA and review privileged access assignments")
        if "logging" in categories:
            actions.append("Centralize audit logs and enable alerting for privileged actions")
        if "asset_management" in categories:
            actions.append("Complete asset inventory and assign accountable owners")
        if "vulnerability_management" in categories:
            actions.append("Reduce patching gaps and tighten vulnerability scanning cadence")
        if "incident_response" in categories:
            actions.append("Define and test incident response playbooks")
        if "data_protection" in categories:
            actions.append("Enforce encryption and validate recovery procedures")
        if not actions:
            actions.append("Continue periodic control verification and governance reviews")
        return actions

    def print_report(self, pretty: bool = True) -> None:
        payload = json.dumps(self.last_report, indent=2 if pretty else None, sort_keys=True)
        print(payload)


class SOCAgentOrchestrator:
    """Coordination layer showing how a compliance specialist fits inside a SOC."""

    def __init__(self, framework: str = "NIST-800-53", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.framework = framework
        self.case_id = case_id
        self.analyst = analyst
        self.compliance_agent = ComplianceAnalysisAgent(framework=framework, case_id=case_id, analyst=analyst)

    def assess_compliance(self, controls: Dict[str, Any]) -> Dict[str, Any]:
        result = self.compliance_agent.analyze_controls(controls)
        return {
            "agent": "soc_orchestrator",
            "case_id": self.case_id,
            "compliance_result": result,
            "next_step": "escalate_to_governance" if result["summary"]["classification"] == "non_compliant" else "monitor_and_report",
            "orchestration_plan": {
                "primary_agent": "compliance_analysis",
                "secondary_agents": ["cloud_security", "malware_analysis", "identity_security"],
                "decision": "escalate" if result["summary"]["classification"] == "non_compliant" else "review",
            },
        }


class SOCComplianceWorkflow:
    """Example workflow tying the compliance agent into a larger SOC pipeline."""

    def __init__(self, framework: str = "NIST-800-53", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.orchestrator = SOCAgentOrchestrator(framework=framework, case_id=case_id, analyst=analyst)

    def run(self, controls: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "workflow": "soc_compliance_pipeline",
            "orchestrator": self.orchestrator.assess_compliance(controls),
            "status": "agentic_compliance_triage_complete",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="SOC compliance analysis agent")
    parser.add_argument("--framework", default="NIST-800-53", help="Compliance framework to assess")
    parser.add_argument("--case-id", default="CASE-UNKNOWN", help="SOC case identifier")
    parser.add_argument("--analyst", default="SOC Analyst", help="Analyst or team name")
    parser.add_argument("--json", help="Path to a JSON control file")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON output")
    args = parser.parse_args()

    if not args.json:
        print("[ERROR] Please provide a JSON control file using --json", file=sys.stderr)
        return 1

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            controls = json.load(f)
    except Exception as exc:
        print(f"[ERROR] Could not read controls: {exc}", file=sys.stderr)
        return 2

    try:
        workflow = SOCComplianceWorkflow(framework=args.framework, case_id=args.case_id, analyst=args.analyst)
        result = workflow.run(controls)
        if args.compact:
            print(json.dumps(result, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Analysis failed: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
