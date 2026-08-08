import json
from pathlib import Path
from typing import Dict, Any
from agents.threat_intel import SOCAgentOrchestrator as ThreatIntelAgent
from agents.log_analysis import SOCLogWorkflow
from agents.malware import MalwareAnalysisAgent
from agents.cloud_security import CloudSecurityAgent
from agents.compliance import ComplianceAgent
from agents.sbom_agent import SBOMAnalysisAgent

class SOCAgentOrchestrator:
    def __init__(self, case_id="UNKNOWN", analyst="System"):
        self.case_id = case_id
        self.analyst = analyst
        self.root_dir = Path(__file__).parent.parent

    def _run_threat_intel(self, observables: list) -> dict:
        return ThreatIntelAgent().enrich_case(observables)

    def _run_log_analysis(self, logs: list) -> dict:
        return SOCLogWorkflow().run(logs)

    def _run_malware(self, file_path: str) -> dict:
        return MalwareAnalysisAgent().analyze_file(file_path)

    def _run_cloud_security(self, cloud_config: dict) -> dict:
        return CloudSecurityAgent().assess_cloud_posture(cloud_config)

    def _run_compliance(self, controls: dict) -> dict:
        return ComplianceAgent().assess_compliance(controls)

    def _run_sbom(self, dependencies: dict) -> dict:
        return SBOMAnalysisAgent().run(dependencies)

    def _decide_priority(self, specialists: dict) -> str:
        return "critical_containment"

    def _next_step(self, decision: str) -> str:
        return "isolate_and_block"

    def run_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "orchestrator": {"case_id": self.case_id, "status": "completed"},
            "specialists": {},
            "aggregated_data": {"mitre": [], "tools": [], "actions": [], "predictions": [], "attack_type": "Unknown Vector", "pr_diff": "", "pr_title": ""}
        }

        if incident.get("observables"):
            results["specialists"]["threat_intelligence"] = self._run_threat_intel(incident["observables"])
        if incident.get("logs"):
            results["specialists"]["log_analysis"] = self._run_log_analysis(incident["logs"])
        if incident.get("file_path"):
            results["specialists"]["malware_analysis"] = self._run_malware(incident["file_path"])
        if incident.get("cloud_config"):
            results["specialists"]["cloud_security"] = self._run_cloud_security(incident["cloud_config"])
        if incident.get("controls"):
            results["specialists"]["compliance_analysis"] = self._run_compliance(incident["controls"])
        if incident.get("dependencies"):
            results["specialists"]["sbom_analysis"] = self._run_sbom(incident["dependencies"])

        mitre_set, tool_set, actions_list, predictions, classifications = set(), set(), [], [], []
        pr_title, pr_diff = "", ""
        
        for agent_name, data in results["specialists"].items():
            if not isinstance(data, dict):
                continue
            for key, val in data.items():
                if isinstance(val, dict) and "summary" in val:
                    summary = val["summary"]
                    mitre_set.update(summary.get("mitre_tactics", []))
                    tool_set.update(summary.get("tools_utilized", []))
                    if summary.get("autonomous_action"):
                        actions_list.append(summary["autonomous_action"])
                    if summary.get("threat_prediction"):
                        predictions.append(summary["threat_prediction"])
                    if summary.get("classification") or summary.get("risk_level") or summary.get("status"):
                        classifications.append(summary.get("classification") or summary.get("risk_level") or summary.get("status"))
                    # Extract the PR data specifically from the SBOM agent
                    if summary.get("pr_diff"):
                        pr_diff = summary.get("pr_diff")
                        pr_title = summary.get("pr_title")

        results["aggregated_data"] = {
            "mitre": list(mitre_set),
            "tools": list(tool_set),
            "actions": actions_list,
            "predictions": predictions,
            "attack_type": classifications[0] if classifications else "Advanced Persistent Threat (APT)",
            "pr_diff": pr_diff,
            "pr_title": pr_title
        }
        
        results["decision"] = self._decide_priority(results["specialists"])
        results["recommended_next_step"] = self._next_step(results["decision"])

        return results
