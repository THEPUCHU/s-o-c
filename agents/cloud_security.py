import json
import requests
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.rl_engine import RLMemoryEngine

class CloudSecurityAgent:
    def __init__(self, cloud="aws", case_id="UNKNOWN", analyst="System"):
        self.cloud = cloud
        self.case_id = case_id
        self.rl_engine = RLMemoryEngine()

    def _get_cloudflare_posture(self) -> dict:
        """Fetches live WAF Security Level from Cloudflare API."""
        token = st.secrets.get("CLOUDFLARE_API_TOKEN")
        zone_id = st.secrets.get("CLOUDFLARE_ZONE_ID")
        
        if not token or not zone_id:
            return {"error": "Cloudflare credentials missing from secrets.", "simulated_waf_level": "medium"}
            
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # E.g., 'essentially_off', 'low', 'medium', 'high', 'under_attack'
                waf_level = response.json().get("result", {}).get("value", "unknown")
                return {"cloudflare_status": "success", "live_waf_level": waf_level}
            else:
                return {"cloudflare_status": "failed", "code": response.status_code, "details": response.text}
        except Exception as e:
            return {"error": str(e)}

    def assess_cloud_posture(self, cloud_config: dict) -> dict:
        if not cloud_config:
            return {}
            
        # 1. Fetch live Cloudflare WAF Posture
        cf_data = self._get_cloudflare_posture()
            
        try:
            historical_guidance = self.rl_engine.get_best_action("cloud_exposure")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = SystemMessage(content=(
                "You are a Cloud Security Posture Management (CSPM) AI integrated with live Cloudflare API telemetry. "
                f"LIVE CLOUDFLARE WAF STATUS: {json.dumps(cf_data)}. "
                f"HISTORICAL RL DATA: Past highest rewarded action: '{historical_guidance}'. "
                "Evaluate the AWS/GCP config alongside the Cloudflare edge status. "
                "You MUST output raw JSON matching this exact schema: "
                "{"
                "  \"cloud_security_result\": {"
                "    \"summary\": {"
                "      \"risk_level\": \"critical\", "
                "      \"classification\": \"Cloud Infrastructure & Edge Exposure\", "
                "      \"mitre_tactics\": [\"T1190 - Exploit Public-Facing Application\"], "
                "      \"tools_utilized\": [\"Cloudflare API v4\", \"AWS CloudTrail\"], "
                "      \"autonomous_action\": \"Escalate Cloudflare WAF to 'I m Under Attack' mode & Revoke IAM roles\", "
                "      \"threat_prediction\": \"Attacker will attempt to bypass WAF to dump S3 buckets containing PII.\""
                "    }"
                "  }"
                "}"
            ))
            
            user_msg = HumanMessage(content=f"Audit this config: {json.dumps(cloud_config)}")
            response = llm.invoke([sys_msg, user_msg])
            
            return json.loads(response.content.strip().strip('```json').strip('```'))
            
        except Exception as e:
            return {"error": str(e)}

    # Aliases for method names
    def _run_cloud(self, cloud_config: dict) -> dict:
        return self.assess_cloud_posture(cloud_config)

    def run(self, cloud_config: dict) -> dict:
        return self.assess_cloud_posture(cloud_config)

# Class Alias so both class names work seamlessly
SOCAgentOrchestrator = CloudSecurityAgent
