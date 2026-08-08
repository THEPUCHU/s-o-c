import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class ComplianceAgent:
    def __init__(self, case_id="UNKNOWN", analyst="System"):
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def _run_compliance(self, controls: dict) -> dict:
        if not controls:
            return {}
            
        try:
            historical_guidance = self.rl_engine.get_best_action("compliance_drift")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an active Compliance & Audit AI. Evaluate the security controls. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"compliance_result\": {"
                "    \"summary\": {"
                "      \"status\": \"non_compliant\", "
                "      \"mitre_tactics\": [\"T1489 - Service Stop\"], "
                "      \"tools_utilized\": [\"NIST 800-53 Framework Tracker\"], "
                "      \"autonomous_action\": \"Enforce global MFA policy across all tenants\", "
                "      \"threat_prediction\": \"Regulatory fines likely if data exfiltration is not contained in 24 hours.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Evaluate these controls: {json.dumps(controls)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}
