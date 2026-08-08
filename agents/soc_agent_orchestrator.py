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

    def _trigger_soar_webhook(self, threat_type: str, action: str):
        """Fires a live alert to a Discord/Slack webhook for critical incidents."""
        webhook_url = st.secrets.get("SOAR_WEBHOOK_URL", "")
        if not webhook_url:
            return "Webhook URL not configured in secrets."
            
        # Payload includes 'content' (for Discord) and 'text' (for Slack) for universal compatibility
        payload = {
            "content": f"🚨 **CRITICAL SOC ESCALATION** 🚨\n**Threat:** {threat_type}\n**Recommended Action:** {action}\n**Status:** Awaiting Incident Commander Override.",
            "text": f"🚨 *CRITICAL SOC ESCALATION* 🚨\n*Threat:* {threat_type}\n*Recommended Action:* {action}\n*Status:* Awaiting Incident Commander Override."
        }
        
        try:
            requests.post(webhook_url, json=payload, timeout=3)
            return "Alert dispatched successfully."
        except Exception as e:
            return f"Failed to dispatch alert: {e}"

    def _compute_master_consensus(self, specialists_data: dict) -> dict:
        """Uses Groq to act as the Master Brain, reading all agent outputs to make a final decision."""
        try:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are the Master SOC Orchestrator AI. Read the JSON reports from your specialist agents and determine the final priority and exact containment step. "
                "Output ONLY valid JSON matching this schema: "
                "{\"decision\": \"critical_containment\", \"recommended_next_step\": \"isolate_host\"}"
            ))
            
            user_msg = HumanMessage(content=f"Synthesize these agent reports: {json.dumps(specialists_data)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('
