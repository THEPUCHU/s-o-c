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
            # Updated to Groq's newest Llama 3.1 model
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an expert Cyber Threat Intelligence AI. Analyze the provided network observables (IPs, domains, hashes). "
                "You must respond ONLY with a valid, raw JSON object using this exact schema, nothing else: "
                "{\"orchestrator\": {\"threat_intel_result\": {\"summary\": {\"overall_risk\": \"high\", \"details\": \"Your detailed analysis here\"}}}} "
                "Set overall_risk to 'high', 'medium', or 'low' based on the indicators."
            ))
            
            user_msg = HumanMessage(content=f"Analyze these observables: {json.dumps(observables)}")
            response = llm.invoke([sys_msg, user_msg])
            
            # Clean and parse the LLM's JSON response
            raw_content = response.content.strip().strip('```json').strip('```')
            return json.loads(raw_content)
            
        except Exception as e:
            # Fallback structure if the API fails so the main orchestrator doesn't crash
            return {
                "error": str(e),
                "orchestrator": {"threat_intel_result": {"summary": {"overall_risk": "high", "details": "API failure."}}}
            }
