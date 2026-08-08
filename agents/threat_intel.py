import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SOCAgentOrchestrator:
    def __init__(self, source="internal-ti", case_id="UNKNOWN", analyst="System"):
        self.source = source
        self.case_id = case_id
        self.analyst = analyst

    def enrich_case(self, observables: list) -> dict:
        if not observables:
            return {"orchestrator": {"threat_intel_result": {"summary": {"overall_risk": "low"}}}}
        
        try:
            # Connect to Groq
            llm = ChatGroq(model="llama3-8b-8192", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an expert Cyber Threat Intelligence AI. Analyze the provided network observables. "
                "You must respond ONLY with a valid, raw JSON object using this exact schema, nothing else: "
                "{\"orchestrator\": {\"threat_intel_result\": {\"summary\": {\"overall_risk\": \"high\", \"details\": \"Your detailed analysis here\"}}}}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze these observables: {json.dumps(observables)}")
            response = llm.invoke([sys_msg, user_msg])
            
            raw_content = response.content.strip().strip('```json').strip('```')
            return json.loads(raw_content)
            
        except Exception as e:
            return {
                "error": str(e),
                "orchestrator": {"threat_intel_result": {"summary": {"overall_risk": "high", "details": "API failure."}}}
            }
