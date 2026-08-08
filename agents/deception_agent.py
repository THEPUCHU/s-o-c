import json
import uuid
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class DeceptionAgent:
    def __init__(self, case_id="UNKNOWN"):
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def generate_honeytoken(self, threat_context: dict) -> dict:
        """Dynamically designs a deception trap (Honeytoken) based on the attacker's TTPs."""
        if not threat_context:
            return {}
            
        try:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an Active Defense & Deception AI. Your job is to generate Honeytokens "
                "(decoy assets) to trap attackers based on their current behavior. "
                "Output ONLY valid JSON matching this schema: "
                "{"
                "  \"deception_analysis\": {"
                "    \"summary\": {"
                "      \"trap_type\": \"AWS_IAM_Honeytoken\","
                "      \"deployment_location\": \"/root/.aws/credentials\","
                "      \"tools_utilized\": [\"Canarytokens API\", \"Active Defense Orchestrator\"],"
                "      \"autonomous_action\": \"Deploy Fake AWS IAM Keys to trap attacker\","
                "      \"trap_configuration\": {\"AccessKeyId\": \"AKIAIOSFODNN7EXAMPLE\", \"SecretAccessKey\": \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"}"
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Design a trap for this threat context: {json.dumps(threat_context)}")
            response = llm.invoke([sys_msg, user_msg])
            
            data = json.loads(response.content.strip().strip('```json').strip('```'))
            
            # Inject a realistic looking unique tracking ID
            if "deception_analysis" in data and "summary" in data["deception_analysis"]:
                data["deception_analysis"]["summary"]["trap_configuration"]["Token_ID"] = f"canary_trap_{uuid.uuid4().hex[:8]}"
            
            return data
            
        except Exception as e:
            return {"error": str(e)}

    def run(self, threat_context: dict) -> dict:
        return self.generate_honeytoken(threat_context)
