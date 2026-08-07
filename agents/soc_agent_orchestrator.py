"""Unified SOC agent orchestrator.

This module coordinates the specialist SOC agents for:
- malware analysis
- cloud security posture
- compliance review
- threat intelligence enrichment
- log analysis

The orchestrator loads each specialist module dynamically from the workspace and
runs them when their corresponding data is present in the incident payload.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_python_module(file_path: str | Path, module_name: str) -> Any:
    """Load a Python module from a file path without requiring importable names."""
    path = Path(file_path).resolve()
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SOCAgentOrchestrator:
    """Master Orchestrator for a multi-specialist SOC agentic workflow."""

    def __init__(self, case_id: str = "SOC-CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.case_id = case_id
        self.analyst = analyst
        self.root_dir = Path(__file__).resolve().parent

    def _load_specialist(self, slug: str, file_name: str) -> Any:
        target = self.root_dir / file_name
        if not target.exists():
            raise FileNotFoundError(f"Specialist file not found: {target}")
        return load_python_module(target, f"soc_{slug}")

    def _run_malware(self, file_path: str) -> Optional[Dict[str, Any]]:
        module = self._load_specialist("malware", "malware.py")
        agent = module.MalwareAnalysisAgent(case_id=self.case_id, analyst=self.analyst)
        return agent.analyze_file(file_path)

    def _run_cloud(self, cloud_config: Dict[str, Any], cloud: str = "aws") -> Optional[Dict[str, Any]]:
        module = self._load_specialist("cloud_security", "cloud security.py")
        orchestrator = module.SOCAgentOrchestrator(cloud=cloud, case_id=self.case_id, analyst=self.analyst)
        return orchestrator.assess_cloud_posture(cloud_config)

    def _run_compliance(self, controls: Dict[str, Any], framework: str = "NIST-800-53") -> Optional[Dict[str, Any]]:
        module = self._load_specialist("compliance", "compliance.py")
        orchestrator = module.SOCAgentOrchestrator(framework=framework, case_id=self.case_id, analyst=self.analyst)
        return orchestrator.assess_compliance(controls)

    def _run_threat_intel(self, observables: List[Dict[str, Any]], source: str = "internal-ti") -> Optional[Dict[str, Any]]:
        module = self._load_specialist("threat_intel", "threat intel.py")
        orchestrator = module.SOCAgentOrchestrator(source=source, case_id=self.case_id, analyst=self.analyst)
        return orchestrator.enrich_case(observables)

    def _run_log_analysis(self, logs: List[str]) -> Optional[Dict[str, Any]]:
        module = self._load_specialist("log_analysis", "log analysis.py")
        workflow = module.SOCLogWorkflow(case_id=self.case_id, analyst=self.analyst)
        return workflow.run(logs)

    def run_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all available specialist agents for the supplied incident data."""
        results: Dict[str, Any] = {
            "orchestrator": {
                "agent": "soc_orchestrator",
                "case_id": self.case_id,
                "analyst": self.analyst,
                "status": "completed",
            },
            "specialists": {},
        }

        malware_path = incident.get("file_path") or incident.get("malware_file")
        if malware_path:
            try:
                results["specialists"]["malware_analysis"] = self._run_malware(str(malware_path))
            except Exception as exc:  # pragma: no cover
                results["specialists"]["malware_analysis"] = {"status": "error", "error": str(exc)}

        cloud_config = incident.get("cloud_config") or incident.get("cloud")
        if cloud_config:
            try:
                results["specialists"]["cloud_security"] = self._run_cloud(cloud_config, incident.get("cloud", "aws"))
            except Exception as exc:  # pragma: no cover
                results["specialists"]["cloud_security"] = {"status": "error", "error": str(exc)}

        controls = incident.get("controls") or incident.get("compliance_controls")
        if controls:
            try:
                results["specialists"]["compliance_analysis"] = self._run_compliance(controls, incident.get("framework", "NIST-800-53"))
            except Exception as exc:  # pragma: no cover
                results["specialists"]["compliance_analysis"] = {"status": "error", "error": str(exc)}

        observables = incident.get("observables") or incident.get("threat_intel")
        if observables:
            try:
                results["specialists"]["threat_intelligence"] = self._run_threat_intel(observables, incident.get("source", "internal-ti"))
            except Exception as exc:  # pragma: no cover
                results["specialists"]["threat_intelligence"] = {"status": "error", "error": str(exc)}

        logs = incident.get("logs") or incident.get("log_data")
        if logs:
            try:
                results["specialists"]["log_analysis"] = self._run_log_analysis(logs)
            except Exception as exc:  # pragma: no cover
                results["specialists"]["log_analysis"] = {"status": "error", "error": str(exc)}

        if not results["specialists"]:
            results["specialists"]["status"] = "no_specialist_input_provided"

        results["decision"] = self._decide_priority(results["specialists"])
        results["recommended_next_step"] = self._next_step(results["decision"])
        return results

    def _decide_priority(self, specialists: Dict[str, Any]) -> str:
        if not specialists:
            return "monitor"

        risk_flags = []
        for name, result in specialists.items():
            if not isinstance(result, dict):
                continue
            if name == "malware_analysis":
                category = result.get("summary", {}).get("classification")
                if category == "likely_malicious":
                    risk_flags.append("malware")
            elif name == "cloud_security":
                classification = result.get("cloud_security_result", {}).get("summary", {}).get("classification")
                if classification in {"high_risk", "critical_risk"}:
                    risk_flags.append("cloud")
            elif name == "compliance_analysis":
                classification = result.get("compliance_result", {}).get("summary", {}).get("classification")
                if classification == "non_compliant":
                    risk_flags.append("compliance")
            elif name == "threat_intelligence":
                risk = result.get("orchestrator", {}).get("threat_intel_result", {}).get("summary", {}).get("overall_risk")
                if risk == "high":
                    risk_flags.append("threat")
            elif name == "log_analysis":
                workflow = result.get("orchestrator", {})
                risk = workflow.get("log_analysis_result", {}).get("summary", {}).get("risk_level")
                if risk == "high":
                    risk_flags.append("logs")

        if any(flag in risk_flags for flag in ["malware", "cloud", "logs", "threat"]):
            return "escalate"
        if "compliance" in risk_flags:
            return "governance_review"
        return "monitor"

    def _next_step(self, decision: str) -> str:
        mapping = {
            "escalate": "escalate_to_ir",
            "governance_review": "notify_governance_and_incident_response",
            "monitor": "continue_monitoring_and_collect_more_evidence",
        }
        return mapping.get(decision, "continue_monitoring_and_collect_more_evidence")


def sample_incident() -> Dict[str, Any]:
    """Return a realistic SOC sample payload across all specialist domains."""
    return {
        "case_id": "SOC-900",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T10:00:00Z event=LoginFailed user=admin src=10.0.0.10",
            "2026-08-08T10:05:00Z event=PowerShell execution user=svc_admin src=10.0.0.20",
            "2026-08-08T10:06:00Z event=RemoteDesktop login denied user=ops src=10.0.0.30",
        ],
        "observables": [
            {"value": "198.51.100.10", "type": "ip", "severity": "high"},
            {"value": "malware.example", "type": "domain", "severity": "high"},
            {"value": "abc123def456", "type": "hash", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {
                "root_user_enabled": True,
                "policies": [{"name": "admin-policy", "statements": [{"effect": "Allow", "action": "*", "resource": "*"}]}],
            },
            "storage": {
                "buckets": [{"name": "public-bucket", "public_access": True, "encryption": "disabled"}],
            },
            "network": {
                "security_groups": [{"name": "web-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "22"}]}],
            },
            "logging": {"cloudtrail_enabled": False, "guardduty_enabled": False},
            "secrets": {"values": [{"name": "db-pass", "hardcoded": True}]},
            "compute": {
                "instances": [{"name": "public-host", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]
            },
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 20, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified SOC agent orchestrator")
    parser.add_argument("--json", help="Path to a JSON incident file. If omitted, a sample incident is used.")
    parser.add_argument("--case-id", default="SOC-CASE-UNKNOWN", help="SOC case identifier")
    parser.add_argument("--analyst", default="SOC Analyst", help="Analyst or team name")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON output")
    args = parser.parse_args()

    try:
        if args.json:
            with open(args.json, "r", encoding="utf-8") as handle:
                incident = json.load(handle)
        else:
            incident = sample_incident()

        incident.setdefault("case_id", args.case_id)
        incident.setdefault("analyst", args.analyst)

        orchestrator = SOCAgentOrchestrator(case_id=incident["case_id"], analyst=incident["analyst"])
        result = orchestrator.run_incident(incident)
        if args.compact:
            print(json.dumps(result, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Orchestration failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
