import json
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class SOCAgentOrchestrator:
    def __init__(self, source="internal-ti", case_id="UNKNOWN", analyst="System"):
        self.source = source
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def enrich_case(self, observables: list) -> dict:
        if not observables:
            return {}
        
        try:
            # Check RL memory for past successful actions against IPs/Hashes
            historical_guidance = self.rl_engine.get_best_action("ip_threat")
            
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an active Cyber Threat Intelligence AI with self-learning capabilities. "
                f"HISTORICAL RL DATA: For this threat type, the highest rewarded past action was: '{historical_guidance}'. "
                "Use this to adjust your confidence. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"threat_intel_result\": {"
                "    \"summary\": {"
                "      \"overall_risk\": \"high\", "
                "      \"mitre_tactics\": [\"T1071 - Application Layer Protocol\"], "
                "      \"tools_utilized\": [\"VirusTotal API\"], "
                "      \"autonomous_action\": \"Null-route IP\", "
                "      \"rl_confidence_adjustment\": \"+5% due to past success mapping\", "
                "      \"threat_prediction\": \"Based on the C2 beacon, the attacker's NEXT likely move is T1048 Data Exfiltration. Recommend preemptive DLP block.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze these observables: {json.dumps(observables)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}
