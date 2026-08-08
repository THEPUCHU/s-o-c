import requests
import streamlit as st

class AlertAgent:
    def __init__(self, topic="soc_alerts_hackathon_99"):
        # 🛑 ENSURE THIS MATCHES YOUR NTFY APP TOPIC 🛑
        self.topic = topic
        self.url = f"https://ntfy.sh/{self.topic}"

    def send_alert(self, threat_type: str, action: str):
        """Fires a live push notification to the configured ntfy.sh topic."""
        # We can keep emojis in the message body, and we force utf-8 encoding just to be safe
        message_str = f"🚨 CRITICAL SOC ESCALATION\nThreat: {threat_type}\nAction: {action}"
        message_bytes = message_str.encode('utf-8')
        
        headers = {
            "Title": "SOC AI Swarm Alert", # <-- EMOJI REMOVED FROM HEADER HERE
            "Priority": "urgent",
            "Tags": "rotating_light,skull" # ntfy will read this and add the 🚨 and 💀 automatically!
        }
        
        try:
            print(f"📡 [AlertAgent] Attempting to contact {self.url}...")
            # Pass the utf-8 encoded bytes to the data parameter
            res = requests.post(self.url, data=message_bytes, headers=headers, timeout=5)
            
            if res.status_code == 200:
                print(f"✅ [AlertAgent] Push notification successfully delivered!")
                # Visual confirmation in the Streamlit UI
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
