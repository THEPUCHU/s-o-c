import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        self.topic = topic
        self.url = "https://ntfy.sh"

    def send_alert(self, threat_type: str, action: str):
        payload = {
            "topic": self.topic,
            "title": "CRITICAL SOC ESCALATION",
            "message": f"Threat: {threat_type}\nAction: {action}",
            "tags": ["rotating_light", "skull"],
            "priority": 5
        }
        
        try:
            res = requests.post(self.url, json=payload, timeout=5)
            
            if res.status_code == 200:
                if hasattr(st, "toast"):
                    # NO icon parameter to prevent latin-1 crash
                    st.toast("Push notification sent successfully!")
                return True
            else:
                if hasattr(st, "toast"):
                    st.toast(f"Alert failed: HTTP {res.status_code}")
                return False
                
        except Exception as e:
            if hasattr(st, "toast"):
                st.toast(f"Alert Error: {str(e)}")
            return False
