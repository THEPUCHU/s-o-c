import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCLogWorkflow:
    def __init__(self, case_id="UNKNOWN", analyst="Autonomous Swarm"):
        self.case_id = case_id
        self.analyst = analyst

    def run(self, logs: list) -> dict:
        if not logs:
            return {"orchestrator": {"log_analysis_result": {"summary": {"risk_level": "low"}}}}
        try:
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = SystemMessage(content=(
                "You are an Autonomous SOC Log AI. Analyze these logs for attack patterns and lateral movement. "
                "Respond ONLY with a valid JSON object: "
                "{\"orchestrator\": {\"log_analysis_result\": {\"summary\": {\"risk_level\": \"high\", \"autonomous_action\": \"Terminate active sessions & isolate host network\"}}}}"
            ))
            user_msg = HumanMessage(content=f"Analyze logs: {json.dumps(logs)}")
            response = llm.invoke([sys_msg, user_msg])
            return json.loads(response.content.strip().strip('```json').strip('```'))
        except Exception as e:
            return {"error": str(e), "orchestrator": {"log_analysis_result": {"summary": {"risk_level": "high"}}}}
