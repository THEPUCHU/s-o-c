import streamlit as st
import time
import json
import sys
import os
from pathlib import Path

# --- PATH ROUTING (DO NOT CHANGE) ---
PROJECT_ROOT = Path(__file__).parent
backend_dir = os.path.join(PROJECT_ROOT, 'src') 
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from agents.soc_agent_orchestrator import SOCAgentOrchestrator
except ImportError:
    pass # Will gracefully fail if backend isn't linked yet, but UI will still render.

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Autonomous SOC Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (THE CYBERPUNK SOC LOOK) ---
st.markdown("""
    <style>
    /* Global Background adjustments for a darker, sleeker feel */
    .stApp { background-color: #0b1120; }
    
    /* Neon glowing metrics */
    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1e293b;
        padding: 15px;
        border-radius: 8px;
        border-top: 3px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Terminal Console Style */
    .terminal-box {
        background-color: #050505;
        color: #10b981;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        height: 350px;
        overflow-y: auto;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    
    /* Threat Level Highlight */
    .threat-critical { color: #ef4444; font-weight: bold; }
    .threat-warn { color: #f59e0b; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- MOCK DATA FOR THE DEMO ---
DEMO_PAYLOAD = {
    "case_id": "SOC-2026-ALPHA",
    "timestamp": "2026-08-08T04:42:08Z",
    "source_ip": "198.51.100.45",
    "event_type": "Multiple Authentication Failures & Unusual Outbound Traffic",
    "affected_asset": "Database Server (10.0.4.15)"
}

# --- HEADER ---
st.title("🛡️ Autonomous SOC Command Center")
st.markdown("*Multi-Agent Threat Triage, Analysis, and Containment Platform*")
st.divider()

# --- SIDEBAR (INCIDENT INJECTION) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/GitHub_Invertocat_Logo.svg/200px-GitHub_Invertocat_Logo.svg.png", width=50)
    st.header("Control Panel")
    
    st.subheader("Incoming Telemetry")
    incident_type = st.selectbox(
        "Select Threat Scenario",
        ["Ransomware Beaconing", "Cloud Credential Theft", "Insider Data Exfiltration"]
    )
    
    raw_json = st.text_area("Raw Event Payload (JSON)", value=json.dumps(DEMO_PAYLOAD, indent=2), height=250)
    
    execute_agents = st.button("🚨 INITIATE MULTI-AGENT TRIAGE", type="primary", use_container_width=True)

# --- MAIN DASHBOARD ---
if execute_agents:
    # Top Row: Live Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="System Status", value="ENGAGED", delta="Agents Active")
    with col2:
        st.metric(label="Threat Level", value="CRITICAL", delta="- Requires Action", delta_color="inverse")
    with col3:
        st.metric(label="Case ID", value=DEMO_PAYLOAD["case_id"])
    with col4:
        st.metric(label="Target Asset", value="DB-01")

    st.markdown("### 🧠 Live Agent Orchestration Graph")
    
    # Middle Row: The Live Terminal & Graph
    t_col1, t_col2 = st.columns([2, 1])
    
    with t_col1:
        terminal_placeholder = st.empty()
        
        # Simulated Agent Output (This makes the demo look incredibly dynamic)
        agent_logs = [
            "[SYSTEM] Initializing SOC Coordinator...",
            "[COORDINATOR] Alert received. Extracting IOCs: '198.51.100.45'.",
            "[COORDINATOR] Fanning out tasks to specialists...",
            "[THREAT_INTEL] Querying external databases for 198.51.100.45...",
            "[LOG_ANALYSIS] Correlating internal logs for DB-01...",
            "[THREAT_INTEL] ⚠️ MATCH FOUND: IP associated with Cobalt Strike C2.",
            "[LOG_ANALYSIS] Found 45 failed SSH logins followed by successful key auth.",
            "[CLOUD_SEC] Checking IAM roles. Target holds S3 Read/Write permissions.",
            "[INCIDENT_RESPONSE] Synthesizing reports. Compiling containment strategy."
        ]
        
        current_log = ""
        for log in agent_logs:
            current_log += log + "<br>"
            terminal_placeholder.markdown(f"<div class='terminal-box'>{current_log}<span class='blink'>_</span></div>", unsafe_allow_html=True)
            time.sleep(0.6) # Fake delay for visual effect

    with t_col2:
        st.markdown("#### 🗺️ Attack Path")
        st.info("**Initial Access:** Brute Force via SSH")
        st.warning("**Execution:** Python payload executed on `DB-01`")
        st.error("**C2:** Outbound beaconing to `198.51.100.45`")
        
        st.divider()
        st.markdown("#### 🛑 Containment Decision")
        human_decision = st.radio(
            "Require Human Override?",
            ["Wait for Analyst Approval", "Auto-Isolate Asset"]
        )
        if st.button("Execute Action"):
            st.toast("Containment Action Triggered!", icon="✅")

    # Bottom Row: Specialist Reports (Tabbed Interface)
    st.markdown("### 📋 Agent Intelligence Reports")
    tab1, tab2, tab3, tab4 = st.tabs(["Threat Intel Agent", "Log Analysis Agent", "Cloud Security Agent", "Containment Plan"])
    
    with tab1:
        st.subheader("External Threat Intelligence")
        st.json({
            "ip_address": "198.51.100.45",
            "reputation_score": "Malicious (98/100)",
            "known_associations": ["Cobalt Strike", "APT29"],
            "geolocation": "Unknown"
        })
    with tab2:
        st.subheader("Internal Log Correlation")
        st.text("Timestamp | Event | Source | Destination | Status")
        st.code("""
        04:40:12 | SSH_FAIL | 198.51.100.45 | 10.0.4.15 | DENIED
        04:40:15 | SSH_FAIL | 198.51.100.45 | 10.0.4.15 | DENIED
        04:41:02 | SSH_AUTH | 198.51.100.45 | 10.0.4.15 | SUCCESS
        04:42:01 | TCP_OUT  | 10.0.4.15     | 198.51.100.45 | ESTABLISHED
        """, language="bash")
    with tab3:
        st.subheader("Cloud Posture Assessment")
        st.write("**Asset:** `DB-01` (EC2 Instance)")
        st.write("**Attached IAM Role:** `db-admin-role` (Over-privileged)")
        st.write("**Recommendation:** Revoke `s3:*` permissions immediately.")
    with tab4:
        st.subheader("Proposed Containment Strategy")
        st.checkbox("1. Null-route 198.51.100.45 at edge firewall.")
        st.checkbox("2. Detach 'db-admin-role' from DB-01 instance.")
        st.checkbox("3. Isolate DB-01 via Security Group lockdown.")
        st.button("Approve & Execute Playbook")

else:
    # Empty State (Before button is clicked)
    st.info("👈 Select a threat scenario from the Control Panel and initiate the multi-agent triage.")
    
    # Placeholder layout so it doesn't look empty
    col1, col2, col3, col4 = st.columns(4)
    for col in [col1, col2, col3, col4]:
        col.metric("Awaiting Data...", "--")
    
    st.markdown("<div class='terminal-box'>System Idle. Waiting for telemetry...</div>", unsafe_allow_html=True)
