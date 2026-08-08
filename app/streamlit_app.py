import streamlit as st
import sys
import json
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
    </style>
""", unsafe_allow_html=True)

def render_agent_card(agent_name, icon, state, is_master=False):
    if state == "idle":
        border, bg, text, status = "#333333", "#111111", "#555555", "💤 Standby"
    elif state == "running":
        border, bg, text, status = "#ff6600", "#331a00", "#ff8c00", "⚡ Processing..."
    elif state == "routing":
        border, bg, text, status = "#3b82f6", "#172554", "#60a5fa", "📡 Routing Tasks..."
    elif state == "consensus":
        border, bg, text, status = "#a855f7", "#3b0764", "#c084fc", "⚖️ Computing Consensus..."
    else: 
        border, bg, text, status = "#10b981", "#022c22", "#34d399", "✅ Deployed"

    box_shadow = f"box-shadow: 0 0 15px {border}40;" if is_master else ""

    return f"""
    <div style="border: 2px solid {border}; background-color: {bg}; padding: 15px; border-radius: 8px; text-align: center; transition: all 0.2s ease; {box_shadow}">
        <div style="font-size: 28px; margin-bottom: 10px;">{icon}</div>
        <h4 style="color: {text}; margin: 0; font-size: 15px;">{agent_name}</h4>
        <div style="color: {text}; font-size: 12px; margin-top: 5px;">{status}</div>
    </div>
    """

# --- THREAT SCENARIOS DICTIONARY ---
scenarios = {
    "External Cloud Breach": {
        "ip": "198.51.100.45",
        "file": "C:\\Windows\\Temp\\svchost_sus.exe",
        "cloud_env": "AWS (Root IAM Enabled)",
        "logs": ["2026-08-08 LoginFailed src=198.51.100.45", "2026-08-08 PowerShell execution"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "actions": "> Null-routing IP 198.51.100.45... <span class='success-text'>SUCCESS</span><br>> Quarantining svchost_sus.exe... <span class='success-text'>SUCCESS</span><br>> Revoking AWS Root Access... <span class='success-text'>SUCCESS</span>",
        "nodes": ["External Threat<br>IP: 198.51.100.45", "Exposed Cloud Asset<br>Root IAM Enabled", "Lateral Movement<br>svchost_sus.exe"]
    },
    "Ransomware Outbreak": {
        "ip": "203.0.113.88",
        "file": "C:\\Users\\Admin\\Downloads\\invoice_pdf.exe",
        "cloud_env": "Azure (Blob Storage Target)",
        "logs": ["2026-08-08 Mass file encryption detected", "2026-08-08 Outbound C2 beacon to 203.0.113.88"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "actions": "> Isolating Host from Network... <span class='success-text'>SUCCESS</span><br>> Killing process invoice_pdf.exe... <span class='success-text'>SUCCESS</span><br>> Blocking C2 IP 203.0.113.88 at Firewall... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Phishing Payload<br>invoice_pdf.exe", "Mass File Encryption<br>Local Drive", "C2 Beaconing<br>IP: 203.0.113.88"]
    },
    "Insider Data Exfiltration": {
        "ip": "10.0.4.55",
        "file": "/usr/local/bin/db_dump.sh",
        "cloud_env": "GCP (Unauthorized DB Snapshot)",
        "logs": ["2026-08-08 Massive DB read volume by User:jdoe", "2026-08-08 Snapshot exported to external bucket"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "actions": "> Disabling AD Account 'jdoe'... <span class='success-text'>SUCCESS</span><br>> Terminating active DB sessions... <span class='success-text'>SUCCESS</span><br>> Deleting unauthorized GCP snapshot... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Internal Account<br>User: jdoe", "Unauthorized Script<br>db_dump.sh", "Data Exfiltration<br>External Bucket"]
    }
}

# --- HEADER ---
st.title("🔥 Autonomous SOC AI")
st.caption("Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ Mission Control")
    st.success("🟢 Autonomous Engine: ONLINE")
    st.divider()
    
    selected_scenario = st.selectbox("Select Threat Scenario:", list(scenarios.keys()))
    s_data = scenarios[selected_scenario]
    
    run_workflow = st.button("▶ Execute Agentic Response", type="primary", use_container_width=True)

# --- NEURAL SWARM TRACKER ---
st.subheader("🤖 Neural Swarm Activity Tracker")

# 1. Top Tier: The Orchestrator
col_spacer1, col_orch, col_spacer2 = st.columns([1.5, 2, 1.5])
ui_orchestrator = col_orch.empty()
ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "idle", is_master=True), unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #555; font-size: 24px; margin-bottom: -10px;'>⬇</div>", unsafe_allow_html=True)

# 2. Bottom Tier: The Specialist Agents
c1, c2, c3, c4, c5 = st.columns(5)
ui_malware = c1.empty()
ui_intel = c2.empty()
ui_cloud = c3.empty()
ui_log = c4.empty()
ui_comp = c5.empty()

ui_malware.markdown(render_agent_card("Malware AI", "🦠", "idle"), unsafe_allow_html=True)
ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "idle"), unsafe_allow_html=True)
ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "idle"), unsafe_allow_html=True)
ui_log.markdown(render_agent_card("Log Analysis", "📜", "idle"), unsafe_allow_html=True)
ui_comp.markdown(render_agent_card("Compliance", "📋", "idle"), unsafe_allow_html=True)

st.divider()

# --- PRE-RUN DASHBOARD ---
if not run_workflow:
    st.subheader("🛡️ Environment Readiness Overview")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Monitored Endpoints", value="12,402", delta="Online")
    m2.metric(label="Cloud Assets", value="843", delta="AWS, GCP, Azure")
    m3.metric(label="Active Policies", value="142", delta="NIST-800-53")
    m4.metric(label="Swarm Latency", value="12ms", delta="Optimal", delta_color="normal")
    
    st.divider()
    
    st.subheader("📥 Pending Injection Payload")
    st.info(f"Targeting: {selected_scenario}. The Orchestrator will ingest this data upon deployment.")
    
    st.json({
        "target_ip": s_data["ip"],
        "suspicious_file": s_data["file"],
        "cloud_environment": s_data["cloud_env"],
        "correlated_logs": s_data["logs"]
    })

# --- POST-RUN DASHBOARD ---
if run_workflow and backend_connected:
    live_incident = {
        "file_path": s_data["file"],
        "observables": [{"value": s_data["ip"], "type": "ip", "severity": "high"}],
        "cloud_config": s_data["config"],
        "logs": s_data["logs"],
        "controls": {"mfa_required": False}
    }

    orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE", analyst="Autonomous Swarm")
    final_results = {"specialists": {}}

    with st.spinner("Master Orchestrator has taken control..."):
        
        # Step 1: Orchestrator Ingests & Routes
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "routing", is_master=True), unsafe_allow_html=True)
        
        # Step 2: Agents execute
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "running"), unsafe_allow_html=True)
        final_results["specialists"]["threat_intelligence"] = orchestrator._run_threat_intel(live_incident["observables"])
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "done"), unsafe_allow_html=True)
        
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "running"), unsafe_allow_html=True)
        final_results["specialists"]["log_analysis"] = orchestrator._run_log_analysis(live_incident["logs"])
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "done"), unsafe_allow_html=True)
        
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "running"), unsafe_allow_html=True)
        final_results["specialists"]["malware_analysis"] = orchestrator._run_malware(live_incident["file_path"])
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "done"), unsafe_allow_html=True)
        
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "running"), unsafe_allow_html=True)
        final_results["specialists"]["cloud_security"] = orchestrator._run_cloud(live_incident["cloud_config"])
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "done"), unsafe_allow_html=True)
        
        ui_comp.markdown(render_agent_card("Compliance", "📋", "running"), unsafe_allow_html=True)
        final_results["specialists"]["compliance_analysis"] = orchestrator._run_compliance(live_incident["controls"])
        ui_comp.markdown(render_agent_card("Compliance", "📋", "done"), unsafe_allow_html=True)

        # Step 3: Orchestrator re-takes control to decide final action
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "consensus", is_master=True), unsafe_allow_html=True)
        final_results["decision"] = orchestrator._decide_priority(final_results["specialists"])
        final_results["recommended_next_step"] = orchestrator._next_step(final_results["decision"])
        
        # Final Orchestrator completion
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "done", is_master=True), unsafe_allow_html=True)

    st.success(f"✅ {selected_scenario} Neutralized Autonomously by Orchestrator")
    st.divider()

    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    
    with col1:
        st.markdown("### 🛑 Orchestrator Execution Log")
        action_decision = final_results.get('recommended_next_step', 'isolate_and_block').replace('_', ' ').upper()
        
        st.markdown(f"""
        <div class="action-log">
            [ORCHESTRATOR] Data payload parsed and routed.<br>
            [ORCHESTRATOR] Sub-agent telemetry received.<br>
            [ORCHESTRATOR] Cross-correlating findings...<br>
            [ORCHESTRATOR] Final consensus reached. Bypassing human approval.<br>
            <br>
            > DEPLOYING PLAYBOOK: {action_decision}<br>
            {s_data["actions"]}<br>
            <br>
            [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🕸️ Visual Threat Topography")
        st.markdown(f"""
        <div class="attack-node"><span class="alert-text">{s_data["nodes"][0].split('<br>')[0]}</span><br>{s_data["nodes"][0].split('<br>')[1]}</div>
        <div class="arrow">⬇</div>
        <div class="attack-node"><span class="alert-text">{s_data["nodes"][1].split('<br>')[0]}</span><br>{s_data["nodes"][1].split('<br>')[1]}</div>
        <div class="arrow">⬇</div>
        <div class="attack-node"><span class="alert-text">{s_data["nodes"][2].split('<br>')[0]}</span><br>{s_data["nodes"][2].split('<br>')[1]}</div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("### 🧠 AI Explainability Data")
        
        # Add an expander just for the Orchestrator's final synthesis
        with st.expander("Master Orchestrator Final Decision", expanded=True):
            st.json({
                "computed_priority": final_results["decision"],
                "executed_action": action_decision,
                "agents_utilized": 5
            })
            
        for agent_name, agent_data in final_results.get("specialists", {}).items():
            if isinstance(agent_data, dict) and agent_name != "status":
                with st.expander(f"{agent_name.replace('_', ' ').title()} Output"):
                    st.json(agent_data)
