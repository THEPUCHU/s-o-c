import json
import requests
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class SOCAgentOrchestrator:
    def __init__(self, source="internal-ti", case_id="UNKNOWN", analyst="System"):
        self.source = source
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def _query_virustotal(self, observable_value: str) -> dict:
        api_key = st.secrets.get("VIRUSTOTAL_API_KEY", "")
        if not api_key:
            return {"error": "VirusTotal API key missing from secrets."}
        
        headers = {"x-apikey": api_key}
        if "." in observable_value and not observable_value.startswith("C:\\") and len(observable_value) < 64:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{observable_value}"
        else:
            url = f"https://www.virustotal.com/api/v3/files/{observable_value}"

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {"vt_raw_stats": stats, "status": "success"}
            else:
                return {"status": "not_found_or_rate_limited", "code": response.status_code}
        except Exception as e:
            return {"error": str(e)}

    def enrich_case(self, observables: list) -> dict:
        if not observables:
            return {}
        
        target_val = observables[0].get("value", "198.51.100.45")
        vt_data = self._query_virustotal(target_val)

        try:
            historical_guidance = self.rl_engine.get_best_action("ip_threat")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are an active Cyber Threat Intelligence AI integrated with live VirusTotal data. "
                f"LIVE VIRUSTOTAL RESULTS: {json.dumps(vt_data)}. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"threat_intel_result\": {"
                "    \"summary\": {"
                "      \"overall_risk\": \"high\","
                "      \"classification\": \"External C2 Infrastructure & Malicious IP\","
                "      \"confidence_score\": 98,"
                "      \"mitre_tactics\": [\"T1071 - Application Layer Protocol\"],"
                "      \"tools_utilized\": [\"VirusTotal API v3\", \"AbuseIPDB\"],"
                "      \"autonomous_action\": \"Null-route IP at edge firewall\","
                "      \"threat_prediction\": \"Attacker will rotate to backup infrastructure within 2 hours.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze observable: {target_val}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}

    def _run_threat_intel(self, observables: list) -> dict:
        return self.enrich_case(observables)

    def run(self, observables: list) -> dict:
        return self.enrich_case(observables)
