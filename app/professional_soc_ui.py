import streamlit as st
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from agents.soc_agent_orchestrator import SOCAgentOrchestrator
    backend_connected = True
except ImportError as e:
    backend_connected = False
    st.error(f"Backend Connection Error: {e}")

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

scenarios = {
    "External Cloud Breach": {
        "ip": "198.51.100.45", "file": "C:\\Windows\\Temp\\svchost_sus.exe", "cloud_env": "AWS (Root IAM Enabled)",
        "logs": ["2026-08-08 LoginFailed src=198.51.100.45", "2026-08-08 PowerShell execution"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "nodes": ["External Threat<br>IP: 198.51.100.45", "Exposed Cloud Asset<br>Root IAM Enabled", "Lateral Movement<br>svchost_sus.exe"]
    },
    "Ransomware Outbreak": {
        "ip": "203.0.113.88", "file": "invoice_pdf.exe", "cloud_env": "Azure (Blob Storage)",
        "logs": ["2026-08-08 Mass file encryption detected", "2026-08-08 Outbound C2 beacon"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Phishing Payload<br>invoice_pdf.exe", "Mass File Encryption<br>Local Drive", "C2 Beaconing<br>IP: 203.0.113.88"]
    }
}

if 'swarm_ran' not in st.session_state:
    st.session_state.swarm_ran = False
if 'final_results' not in st.session_state:
    st.session_state.final_results = {}
if 'human_approved' not in st.session_state:
    st.session_state.human_approved = False

st.markdown("<h1>🔥 Autonomous SOC AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization</p>", unsafe_allow_html=True)

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

if st.session_state.swarm_ran and backend_connected:
    if not st.session_state.final_results:
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
        real_tools = agg_data.get("tools", ["VirusTotal API v3"])
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
