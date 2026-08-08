import json
import requests
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class SBOMAnalysisAgent:
    def __init__(self, case_id="UNKNOWN", analyst="System"):
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def _query_osv_api(self, package_name: str, version: str) -> dict:
        """Performs a live query against Google's Open Source Vulnerabilities (OSV) API."""
        url = "https://api.osv.dev/v1/query"
        payload = {
            "version": version,
            "package": {"name": package_name, "ecosystem": "npm"} 
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200 and response.json():
                return {"osv_status": "vulnerabilities_found", "data": response.json()}
            return {"osv_status": "clean", "data": {}}
        except Exception as e:
            return {"error": str(e)}

    def analyze_sbom(self, dependencies: dict) -> dict:
        if not dependencies:
            return {}
            
        # Target the first dependency for the live OSV lookup
        target_pkg = list(dependencies.keys())[0]
        target_ver = dependencies[target_pkg]
        osv_data = self._query_osv_api(target_pkg, target_ver)
            
        try:
            historical_guidance = self.rl_engine.get_best_action("supply_chain")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are a Software Supply Chain & SBOM Security AI. "
                f"LIVE OSV.DEV VULNERABILITY DATA: {json.dumps(osv_data)}. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"sbom_analysis\": {"
                "    \"summary\": {"
                "      \"risk_level\": \"critical\", "
                "      \"mitre_tactics\": [\"T1195 - Supply Chain Compromise\"], "
                "      \"tools_utilized\": [\"OSV.dev Vulnerability API\", \"GitHub GraphQL API\"], "
                "      \"autonomous_action\": \"Generate PR to bump vulnerable dependency\", "
                "      \"threat_prediction\": \"Attacker will attempt to leverage vulnerable package for Remote Code Execution.\","
                "      \"pr_title\": \"[SECURITY] Auto-Patch Vulnerable Dependency\","
                "      \"pr_diff\": \"--- a/package.json\\n+++ b/package.json\\n@@ -10,3 +10,3 @@\\n   \\\"dependencies\\\": {\\n-    \\\"vulnerable-pkg\\\": \\\"^1.0.0\\\",\\n+    \\\"vulnerable-pkg\\\": \\\"^1.0.1\\\"\\n   }\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Analyze SBOM dependency: {target_pkg}@{target_ver}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}

    def run(self, dependencies: dict) -> dict:
        return self.analyze_sbom(dependencies)
