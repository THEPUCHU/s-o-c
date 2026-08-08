import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        # 🛑 ENSURE THIS IS YOUR EXACT NTFY TOPIC 🛑
        self.topic = topic
        self.url = f"https://ntfy.sh/{self.topic}"

    def send_alert(self, threat_type: str, action: str):
        """Fires a live push notification to the configured ntfy.sh topic."""
        message = f"🚨 CRITICAL SOC ESCALATION\nThreat: {threat_type}\nAction: {action}"
        
        headers = {
            "Title": "🚨 SOC AI Swarm Alert",
            "Priority": "urgent",
            "Tags": "rotating_light,skull"
        }
        
        try:
            print(f"📡 [AlertAgent] Attempting to contact {self.url}...")
            res = requests.post(self.url, data=message, headers=headers, timeout=5)
            
            if res.status_code == 200:
                print(f"✅ [AlertAgent] Push notification successfully delivered!")
                if hasattr(st, "toast"):
                    st.toast("📱 Alert Agent successfully pinged your phone!", icon="🚨")
                return True
            else:
                print(f"❌ [AlertAgent] Failed with HTTP {res.status_code}")
                if hasattr(st, "toast"):
                    st.toast(f"⚠️ Alert Agent failed: HTTP {res.status_code}", icon="⚠️")
                return False
                
        except Exception as e:
            print(f"❌ [AlertAgent] Exception encountered: {e}")
            if hasattr(st, "toast"):
                st.toast(f"⚠️ Alert Agent Error: {e}", icon="⚠️")
            return False
