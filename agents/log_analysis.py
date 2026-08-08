import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class SOCLogWorkflow:
    def __init__(self, case_id="UNKNOWN", analyst="System"):
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def _run_log_analysis(self, logs: list) -> dict:
        if not logs:
            return {}
        
        try:
            historical_guidance = self.rl_engine.get_best_action("log_anomaly")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an active SOC Log Analysis AI. Analyze the provided system and network logs. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"log_analysis_result\": {"
                "    \"summary\": {"
                "      \"risk_level\": \"high\", "
                "      \"mitre_tactics\": [\"T1078 - Valid Accounts\", \"T1531 - Account Access Removal\"], "
                "      \"tools_utilized\": [\"Splunk API\", \"Elastic SIEM\"], "
                "      \"autonomous_action\": \"Terminate active user sessions\", "
                "      \"threat_prediction\": \"Attacker will likely attempt lateral movement to Domain Controller next.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze these logs: {json.dumps(logs)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}
