import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCAgentOrchestrator:
    def __init__(self, cloud="aws", case_id="UNKNOWN", analyst="Autonomous Swarm"):
        self.cloud = cloud
        self.case_id = case_id
        self.analyst = analyst

    def assess_cloud_posture(self, cloud_config: dict) -> dict:
        if not cloud_config:
            return {"cloud_security_result": {"summary": {"classification": "low_risk"}}}
        try:
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = SystemMessage(content=(
                "You are an Autonomous Cloud Security AI. Evaluate this cloud config for critical risks (e.g., public buckets, over-privileged IAM). "
                "Respond ONLY with a valid JSON object: "
                "{\"cloud_security_result\": {\"summary\": {\"classification\": \"critical_risk\", \"autonomous_action\": \"Revoke IAM roles & enforce private ACL on S3\"}}}"
            ))
            user_msg = HumanMessage(content=f"Audit this config: {json.dumps(cloud_config)}")
            response = llm.invoke([sys_msg, user_msg])
            return json.loads(response.content.strip().strip('```json').strip('```'))
        except Exception as e:
            return {"error": str(e), "cloud_security_result": {"summary": {"classification": "critical_risk"}}}
