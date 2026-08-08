import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        self.topic = topic
        # For JSON payloads, we post directly to the base URL
        self.url = "https://ntfy.sh"

    def send_alert(self, threat_type: str, action: str):
        # Package everything into a structured dictionary
        # ntfy will automatically read the tags and add the 🚨 and 💀 emojis on your phone
        payload = {
            "topic": self.topic,
            "title": "CRITICAL SOC ESCALATION",
            "message": f"Threat: {threat_type}\nAction: {action}",
            "tags": ["rotating_light", "skull"],
            "priority": 5
        }
        
        try:
            # The json=payload argument forces requests to safely encode the data as utf-8
            # We removed the headers= argument entirely to bypass the latin-1 crash
            res = requests.post(self.url, json=payload, timeout=5)
            
            if res.status_code == 200:
                if hasattr(st, "toast"):
                    st.toast("Push notification sent successfully!", icon="✅")
                return True
            else:
                if hasattr(st, "toast"):
                    st.toast(f"Alert failed: HTTP {res.status_code}", icon="⚠️")
                return False
                
        except Exception as e:
            if hasattr(st, "toast"):
                st.toast(f"Alert Error: {str(e)}", icon="⚠️")
            return False
