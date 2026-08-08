import json
import requests
import streamlit as st
from pathlib import Path
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from agents.threat_intel import SOCAgentOrchestrator as ThreatIntelAgent
from agents.log_analysis import SOCLogWorkflow
from agents.malware import MalwareAnalysisAgent
from agents.cloud_security import CloudSecurityAgent
from agents.compliance import ComplianceAgent
from agents.sbom_agent import SBOMAnalysisAgent
from agents.deception_agent import DeceptionAgent

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

    def _run_deception(self, threat_context: dict) -> dict:
        return DeceptionAgent().run(threat_context)

    def _trigger_soar_webhook(self, threat_type: str, action: str):
        """Fires a live push notification via ntfy.sh and optional Discord/Slack webhook."""
        # 1. ntfy.sh Notification
        topic = "soc_alerts_hackathon_99"  # Replace with your custom ntfy topic name if needed
        url = f"https://ntfy.sh/{topic}"
        message = f"CRITICAL SOC ESCALATION\nThreat: {threat_type}\nAction: {action}"
        
        headers = {
            "Title": "🚨 SOC Swarm Alert",
            "Priority": "urgent",
            "Tags": "rotating_light,skull"
        }
        
        try:
            requests.post(url, data=message, headers=headers, timeout=5)
            if hasattr(st, "toast"):
                st.toast("📱 Mobile Push Notification Dispatched!", icon="🚨")
        except Exception as e:
            print(f"[NTFY ERROR]: {e}")

        # 2. Discord / Slack Webhook Fallback (If configured in secrets)
        webhook_url = st.secrets.get("SOAR_WEBHOOK_URL", "")
        if webhook_url:
            payload = {
                "content": f"🚨 @everyone **CRITICAL SOC ESCALATION** 🚨\n**Threat:** {threat_type}\n**Recommended Action:** {action}\n**Status:** Awaiting Incident Commander Override.",
                "text": f"🚨 @everyone *CRITICAL SOC ESCALATION* 🚨\n*Threat:* {threat_type}\n*Recommended Action:* {action}\n*Status:* Awaiting Incident Commander Override."
            }
            try:
                requests.post(webhook_url, json=payload, timeout=5)
            except Exception as e:
                print(f"[WEBHOOK ERROR]: {e}")

    def _compute_master_consensus(self, specialists_data: dict) -> dict:
        """Uses Groq to act as the Master Brain, synthesizing all 7 agent outputs to form a final verdict."""
        try:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are the Master SOC Orchestrator AI. Read the JSON reports from your 7 specialist agents and determine the final priority and exact containment step. "
                "Output ONLY valid JSON matching this schema: "
                "{\"decision\": \"critical_containment\", \"recommended_next_step\": \"isolate_host\"}"
            ))
            
            user_msg = HumanMessage(content=f"Synthesize these agent reports: {json.dumps(specialists_data)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
        except Exception:
            return {"decision": "critical_containment", "recommended_next_step": "execute_standard_playbook"}

    def run_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "orchestrator": {"case_id": self.case_id, "status": "completed"},
            "specialists": {},
            "aggregated_data": {
                "mitre": [],
                "tools": [],
                "actions": [],
                "predictions": [],
                "attack_type": "Unknown Vector",
                "pr_diff": "",
                "pr_title": ""
            }
        }

        # 1. Dispatch tasks across all 7 agents in the swarm
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
            
        # Run Active Defense & Deception Agent using current context
        results["specialists"]["active_defense"] = self._run_deception({
            "logs": incident.get("logs", []),
            "file": incident.get("file_path", ""),
            "observables": incident.get("observables", [])
        })

        # 2. Aggregate data from all agents for UI display
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
                    if summary.get("pr_diff"):
                        pr_diff = summary.get("pr_diff")
                        pr_title = summary.get("pr_title")

        attack_type = classifications[0] if classifications else "Advanced Persistent Threat (APT)"
        results["aggregated_data"] = {
            "mitre": list(mitre_set),
            "tools": list(tool_set),
            "actions": actions_list,
            "predictions": predictions,
            "attack_type": attack_type,
            "pr_diff": pr_diff,
            "pr_title": pr_title
        }
        
        # 3. Master Brain AI computes final consensus
        consensus = self._compute_master_consensus(results["specialists"])
        results["decision"] = consensus.get("decision", "critical_containment")
        results["recommended_next_step"] = consensus.get("recommended_next_step", "isolate")

        # 4. Dispatch mobile push notification / alert
        self._trigger_soar_webhook(attack_type, results["recommended_next_step"])

        return results
