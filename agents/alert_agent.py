import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        self.url = f"https://ntfy.sh/{topic}"

    def send_alert(self, threat_type: str, action: str):
        try:
            # 1. Aggressively strip ALL emojis and unicode from the incoming text
            safe_threat = str(threat_type).encode('ascii', 'ignore').decode('ascii')
            safe_action = str(action).encode('ascii', 'ignore').decode('ascii')
            
            message = f"CRITICAL SOC ALERT\nThreat: {safe_threat}\nAction: {safe_action}"
            
            # 2. Post the raw data with NO HEADERS whatsoever
            res = requests.post(self.url, data=message, timeout=5)
            
            if res.status_code == 200:
                if hasattr(st, "toast"):
                    st.toast("Push notification sent successfully!")
                return True
            else:
                if hasattr(st, "toast"):
                    st.toast(f"Network failed: HTTP {res.status_code}")
                return False
                
        except Exception as e:
            if hasattr(st, "toast"):
                st.toast(f"Network Error: {str(e)}")
            return False
