import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        self.topic = topic
        self.url = "https://ntfy.sh/" + self.topic

    def send_alert(self, threat_type: str, action: str):
        message = "CRITICAL SOC ESCALATION\nThreat: " + threat_type + "\nAction: " + action
        
        headers = {
            "Title": "SOC AI Swarm Alert",
            "Priority": "urgent"
        }
        
        try:
            res = requests.post(self.url, data=message.encode("utf-8"), headers=headers, timeout=5)
            
            if res.status_code == 200:
                if hasattr(st, "toast"):
                    st.toast("Alert sent to phone successfully.")
                return True
            else:
                if hasattr(st, "toast"):
                    st.toast("Alert failed: HTTP " + str(res.status_code))
                return False
                
        except Exception as e:
            if hasattr(st, "toast"):
                st.toast("Alert Agent Error: " + str(e))
            return False
