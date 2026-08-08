import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class CloudSecurityAgent:
    def __init__(self, cloud="aws", case_id="UNKNOWN", analyst="System"):
        self.cloud = cloud
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def assess_cloud_posture(self, cloud_config: dict) -> dict:
        if not cloud_config:
            return {}
            
        try:
            historical_guidance = self.rl_engine.get_best_action("cloud_exposure")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are a Cloud Security Posture Management (CSPM) AI. Evaluate the AWS/GCP config. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"cloud_security_result\": {"
                "    \"summary\": {"
                "      \"risk_level\": \"critical\", "
                "      \"mitre_tactics\": [\"T1190 - Exploit Public-Facing Application\"], "
                "      \"tools_utilized\": [\"AWS CloudTrail\", \"Pacu\"], "
                "      \"autonomous_action\": \"Revoke exposed IAM roles immediately\", "
                "      \"threat_prediction\": \"Attacker will attempt to dump S3 buckets containing PII.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Audit this config: {json.dumps(cloud_config)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}

    # Aliases for method names
    def _run_cloud(self, cloud_config: dict) -> dict:
        return self.assess_cloud_posture(cloud_config)

    def run(self, cloud_config: dict) -> dict:
        return self.assess_cloud_posture(cloud_config)

# Class Alias so both class names work seamlessly
SOCAgentOrchestrator = CloudSecurityAgent
