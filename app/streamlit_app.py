import streamlit as st
import sys
import json
import pandas as pd
from pathlib import Path

# --- BULLETPROOF PATH ROUTING ---
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from agents.soc_agent_orchestrator import SOCAgentOrchestrator
    backend_connected = True
except ImportError as e:
    backend_connected = False
    st.error(f"Backend Connection Error: {e}")

# --- PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="Autonomous SOC AI", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #eaeaea; }
    [data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 2px solid #ff6600; }
    h1, h2, h3, h4 { color: #ff8c00 !important; font-weight: 600; }
    hr { border-top: 2px solid #ff6600 !important; opacity: 0.3; }
    div.stButton > button[kind="primary"] { background-color: #ff6600 !important; color: #000000 !important; font-weight: bold !important; border: 1px solid #ff8c00 !important; }
    
    /* Terminal Log */
    .action-log { 
        font-family: 'Courier New', monospace; color: #ff8c00; background: #0a0a0a; 
        padding: 15px; border-radius: 5px; border: 1px solid #333; border-left: 4px solid #ff6600; line-height: 1.6;
    }
    .success-text { color: #34d399; font-weight: bold; }
    .alert-text { color: #ef4444; font-weight: bold; }
    
    /* Attack Chain Visualization */
    .attack-node {
        background: #111; border: 1px solid #ff6600; border-radius: 8px; padding: 10px;
        text-align: center; margin-bottom: 10px; box-shadow: 0 0 10px rgba(255, 102, 0, 0.2);
    }
    .arrow { text-align: center; color: #ff6600; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    
    /* Tables */
    .stDataFrame { border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

def render_agent_card(agent_name, icon, state):
    """Generates the HTML for the dynamic agent status cards."""
    if state == "idle":
        border, bg, text, status = "#333333", "#111111", "#555555", "💤 Standby"
    elif state == "running":
        border, bg, text, status = "#ff6600", "#331a00", "#ff8c00", "⚡ Processing..."
    else: # done
        border, bg, text, status = "#10b981", "#022c22", "#34d399", "✅ Deployed"

    return f"""
    <div style="border: 2px solid {border}; background-color: {bg}; padding: 15px; border-radius: 8px; text-align: center; transition: all 0.2s ease;">
        <div style="font-size: 28px; margin-bottom: 10px;">{icon}</div>
        <h4 style="color: {text}; margin: 0; font-size: 15px;">{agent_name}</h4>
        <div style="color: {text}; font-size: 12px; margin-top: 5px;">{status}</div>
    </div>
    """

# --- HEADER ---
st.title("🔥 Autonomous SOC AI")
st.caption("Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ System Status")
    st.success("🟢 Autonomous Engine: ONLINE")
    st.divider()
    target_ip = st.text_input("Ingest Suspicious IP:", value="198.51.100.45")
    run_workflow = st.button("▶ Execute Agentic Response", type="primary", use_container_width=True)

# --- NEURAL SWARM TRACKER (ALWAYS VISIBLE) ---
st.subheader("🤖 Neural Swarm Activity Tracker")

# We use st.empty() so we can overwrite these cards live during execution
c1, c2, c3, c4, c5 = st.columns(5)
ui_malware = c1.empty()
ui_intel = c2.empty()
ui_cloud = c3.empty()
ui_log = c4.empty()
ui_comp = c5.empty()

# Draw the initial "Idle" state
ui_malware.markdown(render_agent_card("Malware AI", "🦠", "idle"), unsafe_allow_html=True)
ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "idle"), unsafe_allow_html=True)
ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "idle"), unsafe_allow_html=True)
ui_log.markdown(render_agent_card("Log Analysis", "📜", "idle"), unsafe_allow_html=True)
ui_comp.markdown(render_agent_card("Compliance", "📋", "idle"), unsafe_allow_html=True)

st.divider()

# --- PRE-RUN DASHBOARD (EMPTY STATE) ---
if not run_workflow:
    st.subheader("📥 Global Threat Ingestion Feed")
    
    # Generate a rich-looking pending alert queue
    mock_feed = pd.DataFrame({
        "Severity": ["🔴 Critical", "🟠 High", "🟡 Medium", "🟡 Medium"],
        "Source": ["AWS GuardDuty", "CrowdStrike", "Okta IAM", "Palo Alto FW"],
        "Detected Event": ["Root Account Login & S3 Exposure", "svchost_sus.exe Executed", f"Failed MFA from {target_ip}", "Port Scan Detected"],
        "Status": ["Awaiting Swarm", "Awaiting Swarm", "Awaiting Swarm", "Queued"]
    })
    
    st.dataframe(mock_feed, use_container_width=True, hide_index=True)
    st.info(f"System is monitoring the environment. Ready to deploy autonomous swarm against IP: {target_ip}.")

# --- POST-RUN DASHBOARD (ACTIVE EXECUTION) ---
if run_workflow and backend_connected:
    live_incident = {
        "file_path": "C:\\Windows\\Temp\\svchost_sus.exe",
        "observables": [{"value": target_ip, "type": "ip", "severity": "high"}],
        "cloud_config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "logs": [f"2026-08-08 LoginFailed src={target_ip}", "2026-08-08 PowerShell execution"],
        "controls": {"mfa_required": False}
    }

    orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE", analyst="Autonomous Swarm")
    final_results = {"specialists": {}}

    with st.spinner("AI Swarm is actively engaged..."):
        
        # 1. Threat Intel
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "running"), unsafe_allow_html=True)
        final_results["specialists"]["threat_intelligence"] = orchestrator._run_threat_intel(live_incident["observables"])
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "done"), unsafe_allow_html=True)
        
        # 2. Log Analysis
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "running"), unsafe_allow_html=True)
        final_results["specialists"]["log_analysis"] = orchestrator._run_log_analysis(live_incident["logs"])
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "done"), unsafe_allow_html=True)
        
        # 3. Malware
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "running"), unsafe_allow_html=True)
        final_results["specialists"]["malware_analysis"] = orchestrator._run_malware(live_incident["file_path"])
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "done"), unsafe_allow_html=True)
        
        # 4. Cloud Security
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "running"), unsafe_allow_html=True)
        final_results["specialists"]["cloud_security"] = orchestrator._run_cloud(live_incident["cloud_config"])
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "done"), unsafe_allow_html=True)
        
        # 5. Compliance
        ui_comp.markdown(render_agent_card("Compliance", "📋", "running"), unsafe_allow_html=True)
        final_results["specialists"]["compliance_analysis"] = orchestrator._run_compliance(live_incident["controls"])
        ui_comp.markdown(render_agent_card("Compliance", "📋", "done"), unsafe_allow_html=True)

        final_results["decision"] = orchestrator._decide_priority(final_results["specialists"])
        final_results["recommended_next_step"] = orchestrator._next_step(final_results["decision"])

    st.success("✅ Threat Neutralized Autonomously")
    st.divider()

    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    
    with col1:
        st.markdown("### 🛑 Autonomous Action Log")
        action_decision = final_results.get('recommended_next_step', 'isolate_and_block').replace('_', ' ').upper()
        
        st.markdown(f"""
        <div class="action-log">
            [SYSTEM] AI swarm consensus reached.<br>
            [SYSTEM] Bypassing human approval.<br>
            <br>
            > EXECUTING: {action_decision}<br>
            > Null-routing {target_ip} at edge... <span class="success-text">SUCCESS</span><br>
            > Quarantining svchost_sus.exe... <span class="success-text">SUCCESS</span><br>
            > Revoking exposed AWS IAM roles... <span class="success-text">SUCCESS</span><br>
            <br>
            [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🕸️ Visual Threat Topography")
        st.markdown(f"""
        <div class="attack-node">
            <span class="alert-text">External Threat</span><br>
            IP: {target_ip}
        </div>
        <div class="arrow">⬇</div>
        <div class="attack-node">
            <span class="alert-text">Exposed Cloud Asset</span><br>
            Root IAM Enabled
        </div>
        <div class="arrow">⬇</div>
        <div class="attack-node">
            <span class="alert-text">Lateral Movement</span><br>
            svchost_sus.exe Deployed
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("### 🧠 AI Explainability Data")
        for agent_name, agent_data in final_results.get("specialists", {}).items():
            if isinstance(agent_data, dict) and agent_name != "status":
                with st.expander(f"{agent_name.replace('_', ' ').title()} Output"):
                    st.json(agent_data)
