import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCAgentOrchestrator:
    def __init__(self, cloud="aws", case_id="UNKNOWN", analyst="System"):
        self.cloud = cloud
        self.case_id = case_id
        self.analyst = analyst

    def assess_cloud_posture(self, cloud_config: dict) -> dict:
        if not cloud_config:
            return {"cloud_security_result": {"summary": {"classification": "low_risk"}}}
            
        try:
            llm = ChatGroq(model="llama3-70b-8192", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are a Cloud Security Posture Management AI. Evaluate the provided cloud infrastructure JSON for misconfigurations (e.g., exposed S3 buckets, excessive IAM privileges). "
                "You must respond ONLY with a valid, raw JSON object using this exact schema: "
                "{\"cloud_security_result\": {\"summary\": {\"classification\": \"critical_risk\", \"vulnerabilities\": [\"vuln 1\", \"vuln 2\"]}}} "
                "Set classification to 'critical_risk', 'high_risk', 'medium_risk', or 'low_risk'."
            ))
            
            user_msg = HumanMessage(content=f"Audit this environment: {json.dumps(cloud_config)}")
            response = llm.invoke([sys_msg, user_msg])
            
            raw_content = response.content.strip().strip('```json').strip('```')
            return json.loads(raw_content)
            
        except Exception as e:
            return {
                "error": str(e),
                "cloud_security_result": {"summary": {"classification": "high_risk", "vulnerabilities": ["Analysis error"]}}
            }
