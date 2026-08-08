import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        # Ensure this matches your ntfy app topic
        self.topic = topic
        self.url = f"https://ntfy.sh/{self.topic}"

    def send_alert(self, threat_type: str, action: str):
        # Absolutely NO emojis in this file to prevent latin-1 codec crashes
        # We explicitly encode the body to utf-8 just to be safe
        message_body = f"CRITICAL SOC ESCALATION\nThreat: {threat_type}\nAction: {action}"
        encoded_message = message_body.encode('utf-8')
        
        headers = {
            "Title": "SOC AI Swarm Alert",
            "Priority": "urgent",
            "Tags": "rotating_light,skull"
        }
        
        try:
            res = requests.post(self.url, data=encoded_message, headers=headers, timeout=5)
            
            if res.status_code == 200:
                if hasattr(st, "toast"):
                    st.toast("Alert Agent successfully pinged your phone!", icon="📱")
                return True
            else:
                if hasattr(st, "toast"):
                    st.toast(f"Alert Agent failed: HTTP {res.status_code}", icon="⚠️")
                return False
                
        except Exception as e:
            if hasattr(st, "toast"):
                st.toast(f"Alert Agent Error: {e}", icon="⚠️")
            return False
