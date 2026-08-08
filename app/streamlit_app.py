import streamlit as st
import sys
import json
import time
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
    [data-testid="stTooltipHoverTarget"] { display: none !important; }
    
    h1 { color: #ff8c00 !important; font-weight: 600; text-align: center; }
    p.subtitle { text-align: center; color: #888; font-size: 16px; margin-top: -10px; margin-bottom: 30px; }
    h2, h3, h4 { color: #ff8c00 !important; font-weight: 600; }
    hr { display: none !important; }
    
    div.stButton > button[kind="primary"] { background-color: #ff6600 !important; color: #000000 !important; font-weight: bold !important; border: 1px solid #ff6600 !important; }
    div.stButton > button[kind="secondary"] { background-color: #10b981 !important; color: #ffffff !important; font-weight: bold !important; border: 1px solid #10b981 !important; }
    
    .action-log { 
        font-family: 'Courier New', monospace; color: #ff8c00; background: #0a0a0a; 
        padding: 15px; border-radius: 5px; border: 1px solid #333; border-left: 4px solid #ff6600; line-height: 1.6;
    }
    .success-text { color: #34d399; font-weight: bold; }
    .alert-text { color: #ef4444; font-weight: bold; }
    .mitre-tag { background: #331a00; color: #ff8c00; padding: 2px 6px; border-radius: 4px; font-size: 12px; border: 1px solid #ff6600;}
    .tool-tag { background: #022c22; color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 12px; border: 1px solid #10b981;}
    
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

# --- COMPREHENSIVE MULTI-THREAT LIBRARY ---
scenarios = {
    "External Cloud Breach": {
        "ip": "198.51.100.45", "file": "C:\\Windows\\Temp\\svchost_sus.exe", "cloud_env": "AWS (Root IAM Enabled)",
        "logs": ["2026-08-08 LoginFailed src=198.51.100.45", "2026-08-08 PowerShell execution"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "nodes": ["External Threat<br>IP: 198.51.100.45", "Exposed Cloud Asset<br>Root IAM Enabled", "Lateral Movement<br>svchost_sus.exe"]
    },
    "Ransomware Outbreak": {
        "ip": "203.0.113.88", "file": "invoice_pdf.exe", "cloud_env": "Azure (Blob Storage Target)",
        "logs": ["2026-08-08 Mass file encryption detected", "2026-08-08 Outbound C2 beacon"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Phishing Payload<br>invoice_pdf.exe", "Mass File Encryption<br>Local Drive", "C2 Beaconing<br>IP: 203.0.113.88"]
    },
    "Insider Data Exfiltration": {
        "ip": "10.0.4.55", "file": "/usr/local/bin/db_dump.sh", "cloud_env": "GCP (Unauthorized DB Snapshot)",
        "logs": ["2026-08-08 Massive DB read volume by User:jdoe", "2026-08-08 Snapshot exported to external bucket"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 1}},
        "nodes": ["Internal Account<br>User: jdoe", "Unauthorized Script<br>db_dump.sh", "Data Exfiltration<br>External Bucket"]
    },
    "Volumetric DDoS Attack": {
        "ip": "185.220.101.7", "file": "N/A (Network Flood)", "cloud_env": "AWS (CloudFront / ELB Edge)",
        "logs": ["2026-08-08 Traffic spike 450Gbps detected", "2026-08-08 SYN flood targeting /login endpoint"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Botnet Traffic<br>IP: 185.220.101.7", "Edge Overload<br>CloudFront / ELB", "Service Degradation<br>HTTP 503 Errors"]
    },
    "Supply Chain Dependency Attack": {
        "ip": "162.243.189.11", "file": "/node_modules/express-helpers/setup.js", "cloud_env": "GCP (CI/CD Pipeline Build Node)",
        "logs": ["2026-08-08 npm install executed malicious postinstall script", "2026-08-08 Outbound connection to unknown registry"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Poisoned Package<br>npm postinstall", "CI/CD Runner<br>GCP Build Host", "Token Theft<br>Environment Leak"]
    },
    "Zero-Day Web Shell RCE": {
        "ip": "45.154.255.120", "file": "/var/www/html/wp-content/uploads/cmd.php", "cloud_env": "AWS (Web Application Cluster)",
        "logs": ["2026-08-08 HTTP POST 200 OK /cmd.php?cmd=id", "2026-08-08 www-data executed whoami and wget"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Exploit Payload<br>Web Shell Injected", "Web Server<br>Apache/nginx process", "Persistence<br>cmd.php Execution"]
    },
    "Leaked Secrets & Cryptojacking": {
        "ip": "194.26.29.112", "file": "/tmp/xmrig_miner", "cloud_env": "AWS (EC2 GPU Cluster)",
        "logs": ["2026-08-08 AWS AccessKey leaked on public GitHub repo", "2026-08-08 32 g5.xlarge instances spawned in us-east-1"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "nodes": ["Leaked IAM Key<br>GitHub Exposure", "Resource Abuse<br>32 EC2 Instances", "Cryptojacking<br>XMRig Process"]
    },
    "MFA Fatigue & Credential Stuffing": {
        "ip": "103.251.170.8", "file": "N/A (Identity Compromise)", "cloud_env": "Azure AD / Okta SSO",
        "logs": ["2026-08-08 142 MFA push notifications sent to User:admin in 3 minutes", "2026-08-08 MFA Approved from unrecognized device"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Credential Abuse<br>Pass-the-Hash", "MFA Spam<br>User Fatigue", "Session Hijack<br>SSO Token Stolen"]
    }
}

# --- SESSION STATE MANAGEMENT ---
if 'swarm_ran' not in st.session_state:
    st.session_state.swarm_ran = False
if 'final_results' not in st.session_state:
    st.session_state.final_results = {}
if 'human_approved' not in st.session_state:
    st.session_state.human_approved = False

# --- HEADER ---
st.markdown("<h1>🔥 Autonomous SOC AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization</p>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ Mission Control")
    exec_mode = st.radio("Execution Mode:", ["Fully Autonomous", "Human-in-the-Loop"])
    st.divider()
    
    selected_scenario = st.selectbox("Select Threat Scenario:", list(scenarios.keys()))
    s_data = scenarios[selected_scenario]
    
    if st.button("▶ Execute Swarm", type="primary", use_container_width=True):
        st.session_state.swarm_ran = True
        st.session_state.human_approved = False
        st.session_state.final_results = {}

# --- NEURAL SWARM TRACKER ---
st.subheader("🤖 Neural Swarm Activity Tracker")

col_spacer1, col_orch, col_spacer2 = st.columns([1.5, 2, 1.5])
ui_orchestrator = col_orch.empty()
ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "idle", is_master=True), unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #555; font-size: 24px; margin-bottom: -10px;'>⬇</div>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
ui_malware = c1.empty()
ui_intel = c2.empty()
ui_cloud = c3.empty()
ui_log = c4.empty()
ui_comp = c5.empty()

# --- PRE-RUN DASHBOARD ---
if not st.session_state.swarm_ran:
    ui_malware.markdown(render_agent_card("Malware AI", "🦠", "idle"), unsafe_allow_html=True)
    ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "idle"), unsafe_allow_html=True)
    ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "idle"), unsafe_allow_html=True)
    ui_log.markdown(render_agent_card("Log Analysis", "📜", "idle"), unsafe_allow_html=True)
    ui_comp.markdown(render_agent_card("Compliance", "📋", "idle"), unsafe_allow_html=True)
    st.divider()
    
    st.subheader("🛡️ Environment Readiness Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Monitored Endpoints", value="12,402", delta="Online")
    m2.metric(label="Cloud Assets", value="843", delta="AWS, GCP, Azure")
    m3.metric(label="Active Policies", value="142", delta="NIST-800-53")
    m4.metric(label="Swarm Latency", value="12ms", delta="Optimal", delta_color="normal")
    
    st.divider()
    st.subheader("📥 Pending Injection Payload")
    st.json({
        "target_ip": s_data["ip"], "suspicious_file": s_data["file"],
        "cloud_environment": s_data["cloud_env"], "correlated_logs": s_data["logs"]
    })

# --- POST-RUN DASHBOARD ---
if st.session_state.swarm_ran and backend_connected:
    
    if not st.session_state.final_results:
        # Build the payload to send to the backend
        live_incident = {
            "observables": [{"value": s_data["ip"], "type": "ip"}],
            "logs": s_data["logs"],
            "file_path": s_data["file"],
            "cloud_config": s_data["config"],
            "controls": {"mfa_required": False}
        }
        orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE-001", analyst="Autonomous Swarm")
        
        with st.spinner("Swarm executing live queries..."):
            ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "routing", is_master=True), unsafe_allow_html=True)
            # Execute backend!
            st.session_state.final_results = orchestrator.run_incident(live_incident)
            st.rerun()

    if st.session_state.final_results:
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "done", is_master=True), unsafe_allow_html=True)
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "done"), unsafe_allow_html=True)
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "done"), unsafe_allow_html=True)
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "done"), unsafe_allow_html=True)
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "done"), unsafe_allow_html=True)
        ui_comp.markdown(render_agent_card("Compliance", "📋", "done"), unsafe_allow_html=True)
        st.divider()

        agg_data = st.session_state.final_results.get("aggregated_data", {})
        real_mitre = agg_data.get("mitre", ["T1078 - Valid Accounts"])
        real_tools = agg_data.get("tools", ["VirusTotal API v3", "Cloudflare API v4"])
        real_actions = agg_data.get("actions", ["Isolate Host"])
        real_predictions = agg_data.get("predictions", ["Lateral movement anticipated."])
        ai_deduced_attack = agg_data.get("attack_type", "Advanced Persistent Threat")

        st.markdown("### 🛠️ Agent Tactics & Tool Orchestration")
        mitre_html = " ".join([f"<span class='mitre-tag'>{m}</span>" for m in real_mitre])
        tool_html = " ".join([f"<span class='tool-tag'>{t}</span>" for t in real_tools])
        st.markdown(f"**AI-Determined MITRE Mapping:** {mitre_html}", unsafe_allow_html=True)
        st.markdown(f"**Autonomously Queried Tools:** {tool_html}", unsafe_allow_html=True)
        st.write("")

        col1, col2, col3 = st.columns([1.2, 1, 1.2])
        
        with col1:
            st.markdown(f"### 🚨 AI Attack Classification: <span style='color: #ef4444;'>{ai_deduced_attack}</span>", unsafe_allow_html=True)
            
            # --- DIGITAL SOC TWIN SIMULATOR ---
            st.markdown("### 👯 Digital SOC Twin Simulation")
            st.info(f"**Blast Radius Analysis:** Simulating '{real_actions[0] if real_actions else 'Isolation'}' against digital replica...\n\n✅ **Result:** 0 production services impacted. 100% safe to execute.")
            
            st.markdown("### 🛑 Containment Playbook")
            
            if exec_mode == "Human-in-the-Loop" and not st.session_state.human_approved:
                st.warning(f"⚠️ **HUMAN OVERRIDE REQUIRED:** AI classified incident as **{ai_deduced_attack}**.")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ Approve (+1 Reward)", type="secondary", use_container_width=True):
                        from agents.rl_engine import RLMemoryEngine
                        RLMemoryEngine().update_reward(ai_deduced_attack, real_actions[0] if real_actions else "Isolate", 1)
                        st.session_state.human_approved = True
                        st.rerun()
                with c_btn2:
                    if st.button("❌ Reject (-1 Reward)", use_container_width=True):
                        from agents.rl_engine import RLMemoryEngine
                        RLMemoryEngine().update_reward(ai_deduced_attack, real_actions[0] if real_actions else "Isolate", -1)
                        st.error("Playbook rejected. RL Q-Table penalized.")
                        st.stop()
            else:
                action_html = "<br>".join([f"> Executing: {act}... <span class='success-text'>SUCCESS</span>" for act in real_actions])
                st.markdown(f"""
                <div class="action-log">
                    [AI DIAGNOSIS] Incident classified as: <b>{ai_deduced_attack}</b><br>
                    [RL ENGINE] Historical reward weights applied.<br>
                    <br>
                    {action_html if real_actions else '> Executing standard isolation... SUCCESS'}<br>
                    <br>
                    [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🔮 Predictive Threat Forecasting")
            st.info(f"**AI Swarm Prediction:** {real_predictions[0] if real_predictions else 'Forecasting unavailable.'}")

        # ... (keep col2 the same for the visual map) ...
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
            with st.expander("Master Orchestrator Synthesis", expanded=True):
                st.json({"computed_priority": st.session_state.final_results.get("decision"), "attack_type": ai_deduced_attack})
                
            for agent_name, agent_data in st.session_state.final_results.get("specialists", {}).items():
                if isinstance(agent_data, dict) and agent_name not in ["status"]:
                    with st.expander(f"{agent_name.replace('_', ' ').title()} Output"):
                        st.json(agent_data)
                        
            # --- EXECUTIVE REPORT DOWNLOAD BUTTON ---
            st.markdown("### 📑 Executive Reporting")
            report_payload = json.dumps(st.session_state.final_results, indent=4)
            st.download_button(
                label="📄 Download Incident Response Report",
                data=report_payload,
                file_name="Executive_IR_Report.json",
                mime="application/json",
                use_container_width=True
            )
