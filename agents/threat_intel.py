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
            return {}
        
        try:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an active Cyber Threat Intelligence AI. Analyze the network observables. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"threat_intel_result\": {"
                "    \"summary\": {"
                "      \"overall_risk\": \"high\", "
                "      \"classification\": \"Short threat name (e.g. C2 Beaconing)\", "
                "      \"confidence_score\": 95, "
                "      \"mitre_tactics\": [\"T1071 - Application Layer Protocol\"], "
                "      \"tools_utilized\": [\"VirusTotal API\", \"AbuseIPDB\"], "
                "      \"reasoning\": \"Explain exactly why this is a threat based on the IP/hash.\", "
                "      \"autonomous_action\": \"Null-route IP at edge firewall\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze these observables: {json.dumps(observables)}")
            response = llm.invoke([sys_msg, user_msg])
            
            raw_content = response.content.strip().strip('```json').strip('```')
            return json.loads(raw_content)
            
        except Exception as e:
            return {"error": str(e)}
