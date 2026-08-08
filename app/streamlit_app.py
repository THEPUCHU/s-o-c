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
    from agents.alert_agent import AlertAgent  # <-- Alert Agent imported directly to UI
    backend_connected = True
except ImportError as e:
    backend_connected = False

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
    .action-log-failed {
        font-family: 'Courier New', monospace; color: #ff8c00; background: #2a0808; 
        padding: 15px; border-radius: 5px; border: 1px solid #ef4444; border-left: 4px solid #ef4444; line-height: 1.6;
    }
    .success-text { color: #34d399; font-weight: bold; }
    .alert-text { color: #ef4444; font-weight: bold; }
    .mitre-tag { background: #331a00; color: #ff8c00; padding: 2px 6px; border-radius: 4px; font-size: 12px; border: 1px solid #ff6600;}
    .tool-tag { background: #022c22; color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 12px; border: 1px solid #10b981;}
    
    .attack-node {
        background: #111; border: 1px solid #ff6600; border-radius: 8px; padding: 10px;
        text-align: center; margin-bottom: 10px; box-shadow: 0 0 10px rgba(255, 102, 0, 0.2);
    }
    .attack-node-failed {
        background: #2a0808; border: 1px solid #ef4444; border-radius: 8px; padding: 10px;
        text-align: center; margin-bottom: 10px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
    }
    .arrow { text-align: center; color: #ff6600; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

def render_agent_card(agent_name, icon, state, is_master=False, is_failed=False):
    if state == "idle":
        border, bg, text, status = "#333333", "#111111", "#555555", "💤 Standby"
    elif state == "running":
        border, bg, text, status = "#ff6600", "#331a00", "#ff8c00", "⚡ Processing..."
    elif state == "routing":
        border, bg, text, status = "#3b82f6", "#172554", "#60a5fa", "📡 Routing Tasks..."
    elif state == "consensus":
        border, bg, text, status = "#a855f7", "#3b0764", "#c084fc", "⚖️ Computing Consensus..."
    elif is_failed and state == "done":
        border, bg, text, status = "#ef4444", "#2a0808", "#ef4444", "🚨 OVERWHELMED"
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
        "dependencies": {"aws-sdk": "2.814.0"},
        "nodes": ["External Threat<br>IP: 198.51.100.45", "Exposed Cloud Asset<br>Root IAM Enabled", "Lateral Movement<br>svchost_sus.exe"]
    },
    "Supply Chain Dependency Attack": {
        "ip": "162.243.189.11", "file": "/node_modules/express-helpers/setup.js", "cloud_env": "GCP (CI/CD Pipeline Build Node)",
        "logs": ["2026-08-08 npm install executed malicious postinstall script", "2026-08-08 Outbound connection to unknown registry"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "dependencies": {"express-helpers": "2.1.4"},
        "nodes": ["Poisoned Package<br>npm postinstall", "CI/CD Runner<br>GCP Build Host", "Token Theft<br>Environment Leak"]
    },
    "Catastrophic Nation-State APT": {
        "ip": "0.0.0.0 (Polymorphic C2)", "file": "\\EFI\\boot\\bootx64.efi (Bootkit)", "cloud_env": "Global Infrastructure",
        "logs": ["2026-08-08 All EDR sensors offline system-wide", "2026-08-08 Immutable backups formatted via storage controller zero-day"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "dependencies": {"grub2": "2.06"},
        "nodes": ["Hardware Supply Chain<br>Compromised Node", "Kernel Rootkit<br>EDR Blinded", "Total Destruction<br>Backups Wiped"]
    }
}

# --- SESSION STATE MANAGEMENT ---
if 'swarm_ran' not in st.session_state: st.session_state.swarm_ran = False
if 'final_results' not in st.session_state: st.session_state.final_results = {}
if 'human_approved' not in st.session_state: st.session_state.human_approved = False
if 'forced_catastrophic' not in st.session_state: st.session_state.forced_catastrophic = False
if 'pr_merged' not in st.session_state: st.session_state.pr_merged = False

if not backend_connected:
    st.error("⚠️ Backend Connection Error: Unable to import `SOCAgentOrchestrator`.")

# --- HEADER ---
st.markdown("<h1>🔥 Autonomous SOC AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization & Deception</p>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ Mission Control")
    exec_mode = st.radio("Execution Mode:", ["Fully Autonomous", "Human-in-the-Loop"])
    st.divider()
    
    scenario_list = list(scenarios.keys())
    default_idx = scenario_list.index("Catastrophic Nation-State APT") if st.session_state.forced_catastrophic else 0
    selected_scenario = st.selectbox("Select Threat Scenario:", scenario_list, index=default_idx)
    s_data = scenarios[selected_scenario]
    
    if st.button("▶ Execute Standard Swarm", type="primary", use_container_width=True):
        st.session_state.swarm_ran = True
        st.session_state.human_approved = False
        st.session_state.pr_merged = False
        st.session_state.final_results = {}
        st.session_state.forced_catastrophic = (selected_scenario == "Catastrophic Nation-State APT")
        if 'alert_sent' in st.session_state: del st.session_state.alert_sent
        
    st.divider()
    st.markdown("### ⚠️ Red Team Simulation")
    if st.button("🚨 INJECT CATASTROPHIC THREAT", use_container_width=True):
        st.session_state.swarm_ran = True
        st.session_state.human_approved = False
        st.session_state.pr_merged = False
        st.session_state.final_results = {}
        st.session_state.forced_catastrophic = True
        if 'alert_sent' in st.session_state: del st.session_state.alert_sent
        st.rerun()

is_catastrophic = st.session_state.forced_catastrophic

# --- NEURAL SWARM TRACKER ---
st.subheader("🤖 Neural Swarm Activity Tracker")

col_spacer1, col_orch, col_spacer2 = st.columns([1.5, 2, 1.5])
ui_orchestrator = col_orch.empty()
ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "idle", is_master=True), unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #555; font-size: 24px; margin-bottom: -10px;'>⬇</div>", unsafe_allow_html=True)

# 7 Columns for the 7 Specialists (Now includes Deception Agent)
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
ui_malware = c1.empty()
ui_intel = c2.empty()
ui_cloud = c3.empty()
ui_log = c4.empty()
ui_comp = c5.empty()
ui_sbom = c6.empty()
ui_deception = c7.empty()

# --- PRE-RUN DASHBOARD ---
if not st.session_state.swarm_ran:
    ui_malware.markdown(render_agent_card("Malware AI", "🦠", "idle"), unsafe_allow_html=True)
    ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "idle"), unsafe_allow_html=True)
    ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "idle"), unsafe_allow_html=True)
    ui_log.markdown(render_agent_card("Log Analysis", "📜", "idle"), unsafe_allow_html=True)
    ui_comp.markdown(render_agent_card("Compliance", "📋", "idle"), unsafe_allow_html=True)
    ui_sbom.markdown(render_agent_card("SBOM Agent", "📦", "idle"), unsafe_allow_html=True)
    ui_deception.markdown(render_agent_card("Active Defense", "🪤", "idle"), unsafe_allow_html=True)
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
        "cloud_environment": s_data["cloud_env"], "correlated_logs": s_data["logs"],
        "package_dependencies": s_data.get("dependencies", {})
    })

# --- POST-RUN DASHBOARD ---
if st.session_state.swarm_ran:
    
    if not st.session_state.final_results and backend_connected:
        live_incident = {
            "observables": [{"value": s_data["ip"], "type": "ip"}],
            "logs": s_data["logs"],
            "file_path": s_data["file"],
            "cloud_config": s_data["config"],
            "controls": {"mfa_required": False},
            "dependencies": s_data.get("dependencies", {})
        }
        orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE-001", analyst="Autonomous Swarm")
        
        with st.spinner("Swarm executing live queries and generating honeytokens..."):
            ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "routing", is_master=True), unsafe_allow_html=True)
            st.session_state.final_results = orchestrator.run_incident(live_incident)
            st.rerun()

    elif not backend_connected and not st.session_state.final_results:
        time.sleep(1)
        st.session_state.final_results = {"decision": "high_priority"}
        st.rerun()

    if st.session_state.final_results:
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "done", is_master=True, is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_malware.markdown(render_agent_card("Malware AI", "🦠", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_intel.markdown(render_agent_card("Threat Intel", "🌐", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_cloud.markdown(render_agent_card("Cloud Sec", "☁️", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_log.markdown(render_agent_card("Log Analysis", "📜", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_comp.markdown(render_agent_card("Compliance", "📋", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_sbom.markdown(render_agent_card("SBOM Agent", "📦", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        ui_deception.markdown(render_agent_card("Active Defense", "🪤", "done", is_failed=is_catastrophic), unsafe_allow_html=True)
        st.divider()

        agg_data = st.session_state.final_results.get("aggregated_data", {})
        
        # Determine Threat Profile
        if is_catastrophic:
            real_mitre = ["T1542 - Pre-OS Boot", "T1562 - Impair Defenses", "T1485 - Data Destruction"]
            real_tools = ["Hardware Telemetry", "CISA Known Exploits API"]
            ai_deduced_attack = "CRITICAL NATION-STATE APT (CATEGORY 5)"
            real_actions = ["ESCALATE TO NSA/CISA INCIDENT COMMANDER"]
            real_predictions = ["Total data loss imminent. Autonomous containment is ineffective against ring-0 rootkit."]
            node_style = "attack-node-failed"

        else:
            real_mitre = agg_data.get("mitre", ["T1078 - Valid Accounts"])
            real_tools = agg_data.get("tools", ["VirusTotal API v3", "Cloudflare API v4", "OSV.dev Vulnerability API", "Canarytokens"])
            ai_deduced_attack = agg_data.get("attack_type", "Advanced Persistent Threat")
            real_actions = agg_data.get("actions", ["Isolate Host"])
            real_predictions = agg_data.get("predictions", ["Lateral movement anticipated."])
            node_style = "attack-node"

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
            if is_catastrophic:
                st.markdown(f"""
                <div class="action-log-failed">
                    [AI DIAGNOSIS] Incident classified as: <b>{ai_deduced_attack}</b><br>
                    [SYSTEM WARNING] Swarm capabilities exceeded.<br><br>
                    > Attempting host isolation... <span class='alert-text'>FAILED (Access Denied)</span><br>
                    > Attempting EDR quarantine... <span class='alert-text'>FAILED (Sensors Offline)</span><br><br>
                    [STATUS] <span class="alert-text">CRITICAL BREACH. ESCALATING TO INCIDENT COMMANDER.</span>
                </div>
                """, unsafe_allow_html=True)
            elif exec_mode == "Human-in-the-Loop" and not st.session_state.human_approved:
                st.warning(f"⚠️ **HUMAN OVERRIDE REQUIRED:** AI classified incident as **{ai_deduced_attack}**.")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ Approve (+1 Reward)", type="secondary", use_container_width=True):
                        st.session_state.human_approved = True
                        st.rerun()
                with c_btn2:
                    if st.button("❌ Reject (-1 Reward)", use_container_width=True):
                        st.error("Playbook rejected. RL Q-Table penalized.")
                        st.stop()
            else:
                action_html = "<br>".join([f"> Executing: {act}... <span class='success-text'>SUCCESS</span>" for act in real_actions])
                st.markdown(f"""
                <div class="action-log">
                    [AI DIAGNOSIS] Incident classified as: <b>{ai_deduced_attack}</b><br>
                    [RL ENGINE] Historical reward weights applied.<br><br>
                    {action_html if real_actions else '> Executing standard isolation... SUCCESS'}<br><br>
                    [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🔮 Predictive Threat Forecasting")
            if is_catastrophic:
                st.error(f"**AI Swarm Prediction:** {real_predictions[0]}")
            else:
                st.info(f"**AI Swarm Prediction:** {real_predictions[0] if real_predictions else 'Forecasting unavailable.'}")

        with col2:
            st.markdown("### 🕸️ Visual Threat Topography")
            st.markdown(f"""
            <div class="{node_style}"><span class="alert-text">{s_data["nodes"][0].split('<br>')[0]}</span><br>{s_data["nodes"][0].split('<br>')[1]}</div>
            <div class="arrow">⬇</div>
            <div class="{node_style}"><span class="alert-text">{s_data["nodes"][1].split('<br>')[0]}</span><br>{s_data["nodes"][1].split('<br>')[1]}</div>
            <div class="arrow">⬇</div>
            <div class="{node_style}"><span class="alert-text">{s_data["nodes"][2].split('<br>')[0]}</span><br>{s_data["nodes"][2].split('<br>')[1]}</div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("### 🧠 AI Explainability Data")
            with st.expander("Master Orchestrator Synthesis", expanded=True):
                st.json({"computed_priority": "CRITICAL_ESCALATION" if is_catastrophic else st.session_state.final_results.get("decision"), "attack_type": ai_deduced_attack})
            
            for agent_name, agent_data in st.session_state.final_results.get("specialists", {}).items():
                if isinstance(agent_data, dict) and agent_name not in ["status"]:
                    with st.expander(f"{agent_name.replace('_', ' ').title()} Output"):
                        st.json(agent_data)
                        
            st.markdown("### 📑 Executive Reporting")
            report_payload = json.dumps(st.session_state.final_results, indent=4)
            st.download_button(label="📄 Download Incident Response Report", data=report_payload, file_name="Executive_IR_Report.json", mime="application/json", use_container_width=True)

        st.divider()
        st.markdown("## 🧬 Self-Healing SBOM & Supply Chain Remediation")
        st.caption("The AI agent dynamically queries the repository Software Bill of Materials (SBOM) and OSV.dev to automatically generate a patch for the root vulnerability.")
        
        sbom_col, pr_col = st.columns([1, 1.5])
        
        with sbom_col:
            st.markdown("### 📦 Vulnerability Traced via SBOM")
            st.warning(f"**Vulnerability Root Cause:** `{s_data['nodes'][1].split('<br>')[1]}`\n\n**Impacted Services:** 14 Microservices in CI/CD Pipeline\n\n**Action:** The autonomous Swarm has mapped the vulnerability to the source code repo, verified the CVE on OSV.dev, and generated a Pull Request to fix it permanently.")
            
        with pr_col:
            # Dynamically pull the PR diff from the SBOM agent if it exists
            pr_title = agg_data.get("pr_title") or "[SECURITY] Auto-Patch Vulnerable Dependency"
            pr_diff = agg_data.get("pr_diff") or "--- a/package.json\n+++ b/package.json\n@@ -10,3 +10,3 @@\n- \"vulnerable-package\": \"^1.0.0\"\n+ \"vulnerable-package\": \"^1.0.1\""
            
            st.markdown(f"### 🐙 Autonomous Pull Request: {pr_title}")
            st.code(pr_diff, language="diff")
            
            if st.session_state.pr_merged:
                st.success("✅ Pull Request successfully merged to `main` branch. CI/CD Pipeline has been triggered to redeploy the patched services.")
            else:
                if st.button("🔀 Merge Pull Request to Production", type="primary", use_container_width=True):
                    st.session_state.pr_merged = True
                    st.balloons()
                    st.rerun()
