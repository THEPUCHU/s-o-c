import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCLogWorkflow:
    def __init__(self, case_id="UNKNOWN", analyst="System"):
        self.case_id = case_id
        self.analyst = analyst

    def run(self, logs: list) -> dict:
        if not logs:
            return {"orchestrator": {"log_analysis_result": {"summary": {"risk_level": "low"}}}}
            
        try:
            llm = ChatGroq(model="llama3-8b-8192", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are a SOC Log Analysis AI. Review the following system logs for anomalies, lateral movement, or brute force attempts. "
                "You must respond ONLY with a valid, raw JSON object using this exact schema: "
                "{\"orchestrator\": {\"log_analysis_result\": {\"summary\": {\"risk_level\": \"high\", \"attack_path\": \"Summary of how the attack progressed\"}}}} "
                "Set risk_level to 'high', 'medium', or 'low'."
            ))
            
            user_msg = HumanMessage(content=f"Correlate these logs: {json.dumps(logs)}")
            response = llm.invoke([sys_msg, user_msg])
            
            raw_content = response.content.strip().strip('```json').strip('```')
            return json.loads(raw_content)
            
        except Exception as e:
            return {
                "error": str(e), 
                "orchestrator": {"log_analysis_result": {"summary": {"risk_level": "high", "attack_path": "Log parsing failed."}}}
            }
