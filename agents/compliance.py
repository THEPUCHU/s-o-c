import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCAgentOrchestrator:
    def __init__(self, framework="NIST", case_id="UNKNOWN", analyst="Autonomous Swarm"):
        self.framework = framework
        self.case_id = case_id
        self.analyst = analyst

    def assess_compliance(self, controls: dict) -> dict:
        if not controls:
            return {"compliance_result": {"summary": {"classification": "compliant"}}}
        try:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = SystemMessage(content=(
                "You are an Autonomous Compliance AI. Evaluate these security controls. "
                "Respond ONLY with a valid JSON object: "
                "{\"compliance_result\": {\"summary\": {\"classification\": \"non_compliant\", \"autonomous_action\": \"Enforce MFA policy organization-wide\"}}}"
            ))
            user_msg = HumanMessage(content=f"Evaluate controls: {json.dumps(controls)}")
            response = llm.invoke([sys_msg, user_msg])
            return json.loads(response.content.strip().strip('```json').strip('```'))
        except Exception as e:
            return {"error": str(e), "compliance_result": {"summary": {"classification": "non_compliant"}}}
