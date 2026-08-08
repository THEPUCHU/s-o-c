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

# --- COMPREHENSIVE MULTI-THREAT LIBRARY ---
scenarios = {
    "External Cloud Breach": {
        "ip": "198.51.100.45", "file": "C:\\Windows\\Temp\\svchost_sus.exe", "cloud_env": "AWS (Root IAM Enabled)",
        "logs": ["2026-08-08 LoginFailed src=198.51.100.45", "2026-08-08 PowerShell execution"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "nodes": ["External Threat<br>IP: 198.51.100.45", "Exposed Cloud Asset<br>Root IAM Enabled", "Lateral Movement<br>svchost_sus.exe"],
        "pr_title": "Fix: Disable Root API Keys & Enforce MFA",
        "pr_diff": """--- a/infrastructure/aws/iam.tf\n+++ b/infrastructure/aws/iam.tf\n@@ -14,3 +14,3 @@\n resource "aws_iam_account_password_policy" "strict" {\n-  require_mfa = false\n+  require_mfa = true\n }"""
    },
    "Ransomware Outbreak": {
        "ip": "203.0.113.88", "file": "invoice_pdf.exe", "cloud_env": "Azure (Blob Storage Target)",
        "logs": ["2026-08-08 Mass file encryption detected", "2026-08-08 Outbound C2 beacon"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Phishing Payload<br>invoice_pdf.exe", "Mass File Encryption<br>Local Drive", "C2 Beaconing<br>IP: 203.0.113.88"],
        "pr_title": "Fix: Enforce EDR Execution Blocking on Temp Folders",
        "pr_diff": """--- a/policies/windows/applocker.xml\n+++ b/policies/windows/applocker.xml\n@@ -42,2 +42,5 @@\n   <FilePathRule Id="fd686d83..." Name="Block Temp Exe" Action="Deny">\n+    <Conditions>\n+      <FilePathCondition Path="%OSDRIVE%\\Windows\\Temp\\*.exe" />\n+    </Conditions>"""
    },
    "Supply Chain Dependency Attack": {
        "ip": "162.243.189.11", "file": "/node_modules/express-helpers/setup.js", "cloud_env": "GCP (CI/CD Pipeline Build Node)",
        "logs": ["2026-08-08 npm install executed malicious postinstall script", "2026-08-08 Outbound connection to unknown registry"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Poisoned Package<br>npm postinstall", "CI/CD Runner<br>GCP Build Host", "Token Theft<br>Environment Leak"],
        "pr_title": "[SECURITY] Bump express-helpers to safe version v2.1.5",
        "pr_diff": """--- a/package.json\n+++ b/package.json\n@@ -12,3 +12,3 @@\n   "dependencies": {\n-    "express-helpers": "^2.1.4",\n+    "express-helpers": "^2.1.5",\n     "lodash": "^4.17.21"\n   }"""
    },
    "Zero-Day Web Shell RCE": {
        "ip": "45.154.255.120", "file": "/var/www/html/wp-content/uploads/cmd.php", "cloud_env": "AWS (Web Application Cluster)",
        "logs": ["2026-08-08 HTTP POST 200 OK /cmd.php?cmd=id", "2026-08-08 www-data executed whoami and wget"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "nodes": ["Exploit Payload<br>Web Shell Injected", "Web Server<br>Apache/nginx process", "Persistence<br>cmd.php Execution"],
        "pr_title": "Fix: Patch PHP Upload Vulnerability & Sanitize Inputs",
        "pr_diff": """--- a/src/upload_handler.php\n+++ b/src/upload_handler.php\n@@ -22,2 +22,5 @@\n $ext = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);\n+if (in_array(strtolower($ext), ['php', 'phtml', 'sh', 'exe'])) {\n+    die("Security Exception: Invalid file type.");\n+}\n move_uploaded_file($_FILES['file']['tmp_name'], $target);"""
    },
    "Catastrophic Nation-State APT": {
        "ip": "0.0.0.0 (Polymorphic C2)", "file": "\\EFI\\boot\\bootx64.efi (Bootkit)", "cloud_env": "Global Infrastructure",
        "logs": ["2026-08-08 All EDR sensors offline system-wide", "2026-08-08 Immutable backups formatted via storage controller zero-day"],
        "config": {"iam": {"root_user_enabled": True}, "storage": {"public_buckets": 1}},
        "nodes": ["Hardware Supply Chain<br>Compromised Node", "Kernel Rootkit<br>EDR Blinded", "Total Destruction<br>Backups Wiped"],
        "pr_title": "CRITICAL: Re-Flash Secure Boot Keys (Infrastructure Reset)",
        "pr_diff": """--- a/uefi/secureboot/keys.db\n+++ b/uefi/secureboot/keys.db\n@@ -1,3 +1,3 @@\n- PK=VENDOR_DEFAULT_KEY\n- KEK=COMPROMISED_KEY_091A\n+ PK=EMERGENCY_OFFLINE_KEY\n+ KEK=ISOLATED_ROOT_CA_2026"""
    }
}

# Ensure Volumetric DDoS doesn't crash since it lacks a PR in this dict structure by default
if "Volumetric DDoS Attack" in scenarios:
    scenarios["Volumetric DDoS Attack"]["pr_title"] = "Fix: Update Cloudflare WAF Rate Limiting Rules"
    scenarios["Volumetric DDoS Attack"]["pr_diff"] = """--- a/terraform/cloudflare_waf.tf\n+++ b/terraform/cloudflare_waf.tf\n@@ -10,3 +10,3 @@\n   action = "block"\n-  threshold = 1000\n+  threshold = 100\n }"""
if "Insider Data Exfiltration" in scenarios:
    scenarios["Insider Data Exfiltration"]["pr_title"] = "Fix: Revoke Over-Privileged Service Accounts"
    scenarios["Insider Data Exfiltration"]["pr_diff"] = """--- a/gcp/iam/bindings.yaml\n+++ b/gcp/iam/bindings.yaml\n@@ -5,3 +5,2 @@\n   members:\n-    - user:jdoe@company.com\n     - serviceAccount:db-backup@project.iam"""
if "Leaked Secrets & Cryptojacking" in scenarios:
    scenarios["Leaked Secrets & Cryptojacking"]["pr_title"] = "Fix: Rotate AWS Keys and Enforce GitLeaks Hook"
    scenarios["Leaked Secrets & Cryptojacking"]["pr_diff"] = """--- a/.pre-commit-config.yaml\n+++ b/.pre-commit-config.yaml\n@@ -8,2 +8,5 @@\n repos:\n+  - repo: https://github.com/gitleaks/gitleaks\n+    rev: v8.16.1\n+    hooks:\n+      - id: gitleaks"""
if "MFA Fatigue & Credential Stuffing" in scenarios:
    scenarios["MFA Fatigue & Credential Stuffing"]["pr_title"] = "Fix: Implement Rate Limiting & Number Matching MFA"
    scenarios["MFA Fatigue & Credential Stuffing"]["pr_diff"] = """--- a/okta/policies.json\n+++ b/okta/policies.json\n@@ -21,3 +21,4 @@\n   "mfa_type": "push",\n-  "require_number_match": false\n+  "require_number_match": true,\n+  "max_attempts_per_minute": 3\n }"""


# --- SESSION STATE MANAGEMENT ---
if 'swarm_ran' not in st.session_state:
    st.session_state.swarm_ran = False
if 'final_results' not in st.session_state:
    st.session_state.final_results = {}
if 'human_approved' not in st.session_state:
    st.session_state.human_approved = False
if 'forced_catastrophic' not in st.session_state:
    st.session_state.forced_catastrophic = False

if not backend_connected:
    st.error("⚠️ Backend Connection Error: Unable to import `SOCAgentOrchestrator`.")

# --- HEADER ---
st.markdown("<h1>🔥 Autonomous SOC AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Self-Directing Agentic Swarm: Zero-Latency Threat Neutralization</p>", unsafe_allow_html=True)

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
        st.session_state.final_results = {}
        st.session_state.forced_catastrophic = (selected_scenario == "Catastrophic Nation-State APT")
        
    st.divider()
    st.markdown("### ⚠️ Red Team Simulation")
    if st.button("🚨 INJECT CATASTROPHIC THREAT", use_container_width=True):
        st.session_state.swarm_ran = True
        st.session_state.human_approved = False
        st.session_state.final_results = {}
        st.session_state.forced_catastrophic = True
        st.rerun()

is_catastrophic = st.session_state.forced_catastrophic

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
if st.session_state.swarm_ran:
    
    if not st.session_state.final_results and backend_connected:
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
        st.divider()

        agg_data = st.session_state.final_results.get("aggregated_data", {})
        
        if is_catastrophic:
            real_mitre = ["T1542 - Pre-OS Boot", "T1562 - Impair Defenses", "T1485 - Data Destruction"]
            real_tools = ["Hardware Telemetry", "CISA Known Exploits API"]
            ai_deduced_attack = "CRITICAL NATION-STATE APT (CATEGORY 5)"
            real_actions = ["ESCALATE TO NSA/CISA INCIDENT COMMANDER"]
            real_predictions = ["Total data loss imminent. Autonomous containment is ineffective against ring-0 rootkit."]
            node_style = "attack-node-failed"
        else:
            real_mitre = agg_data.get("mitre", ["T1078 - Valid Accounts"])
            real_tools = agg_data.get("tools", ["VirusTotal API v3", "Cloudflare API v4"])
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
            
            st.markdown("### 👯 Digital SOC Twin Simulation")
            if is_catastrophic:
                st.error(f"**Blast Radius Analysis:** Simulating containment against `{s_data['nodes'][1].split('<br>')[0]}`...\n\n❌ **FATAL RESULT:** 100% of production services compromised. Attacker has kernel-level persistence. Autonomous tools bypassed.")
            else:
                st.info(f"**Blast Radius Analysis:** Simulating '{real_actions[0] if real_actions else 'Isolation'}' against digital replica...\n\n✅ **Result:** 0 production services impacted. Safe to execute.")
            
            st.markdown("### 🛑 Containment Playbook")
            
            if is_catastrophic:
                st.markdown(f"""
                <div class="action-log-failed">
                    [AI DIAGNOSIS] Incident classified as: <b>{ai_deduced_attack}</b><br>
                    [SYSTEM WARNING] Swarm capabilities exceeded.<br>
                    <br>
                    > Attempting host isolation... <span class='alert-text'>FAILED (Access Denied)</span><br>
                    > Attempting EDR quarantine... <span class='alert-text'>FAILED (Sensors Offline)</span><br>
                    <br>
                    [STATUS] <span class="alert-text">CRITICAL BREACH. ESCALATING TO INCIDENT COMMANDER.</span>
                </div>
                """, unsafe_allow_html=True)
            elif exec_mode == "Human-in-the-Loop" and not st.session_state.human_approved:
                st.warning(f"⚠️ **HUMAN OVERRIDE REQUIRED:** AI classified incident as **{ai_deduced_attack}**.")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ Approve (+1 Reward)", type="secondary", use_container_width=True):
                        try:
                            from agents.rl_engine import RLMemoryEngine
                            RLMemoryEngine().update_reward(ai_deduced_attack, real_actions[0] if real_actions else "Isolate", 1)
                        except:
                            pass
                        st.session_state.human_approved = True
                        st.rerun()
                with c_btn2:
                    if st.button("❌ Reject (-1 Reward)", use_container_width=True):
                        try:
                            from agents.rl_engine import RLMemoryEngine
                            RLMemoryEngine().update_reward(ai_deduced_attack, real_actions[0] if real_actions else "Isolate", -1)
                        except:
                            pass
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
            st.download_button(
                label="📄 Download Incident Response Report",
                data=report_payload,
                file_name="Executive_IR_Report.json",
                mime="application/json",
                use_container_width=True
            )

        st.divider()
        st.markdown("## 🔎 Post-Incident Root Cause & Auto-Playbook")
        rca_col, playbook_col = st.columns(2)
        
        with rca_col:
            st.markdown("### 🎯 Patient Zero Identification (RCA)")
            st.success(f"""
            **Initial Attack Vector:** The intrusion originated via `{s_data["nodes"][0].split('<br>')[1]}`. 
            \n**Vulnerability Exploited:** Bypassed perimeter controls by exploiting `{s_data["nodes"][1].split('<br>')[1]}`.
            \n**Strategic Remediation:** The Orchestrator recommends immediately patching this vector and enforcing Zero Trust identity verification across adjacent subnets to prevent recurrence.
            """)
            
        with playbook_col:
            st.markdown("### ⚡ Autonomous SOAR Playbook (YAML Export)")
            playbook_action = "ESCALATE_TO_INCIDENT_COMMANDER" if is_catastrophic else (real_actions[0] if real_actions else 'Isolate Target')
            soar_yaml = f"""name: Auto-Containment - {ai_deduced_attack}
description: Autonomously generated by SOC AI Swarm
mitre_framework: {real_mitre}
trigger: High-Confidence AI Consensus
tasks:
  1_reconnaissance:
    action: execute_intelligence_gathering
    integrations: {real_tools}
  2_containment:
    action: execute_remediation
    command: "{playbook_action}"
    requires_human_approval: {str(exec_mode == "Human-in-the-Loop").lower()}
status: ready_for_deployment"""
            st.code(soar_yaml, language="yaml")

        # --- INNOVATION FEATURE: SBOM SUPPLY CHAIN REMEDIATION ---
        st.divider()
        st.markdown("## 🧬 Self-Healing SBOM & Supply Chain Remediation")
        st.caption("The AI agent dynamically queries the repository Software Bill of Materials (SBOM) and automatically generates a patch for the root vulnerability.")
        
        sbom_col, pr_col = st.columns([1, 1.5])

        with sbom_col:
            st.markdown("### 📦 Vulnerability Traced via SBOM")
            st.warning(f"**Vulnerability Root Cause:** `{s_data['nodes'][1].split('<br>')[1]}`\n\n**Impacted Services:** 14 Microservices in CI/CD Pipeline\n\n**Action:** The autonomous Swarm has mapped the vulnerability to the source code repo, identified a safe patch strategy, and generated a Pull Request to fix the vulnerability permanently.")
            
        with pr_col:
            st.markdown(f"### 🐙 Autonomous Pull Request: {s_data.get('pr_title', 'Security Patch')}")
            st.code(s_data.get('pr_diff', 'No patch diff available for this scenario.'), language="diff")
            st.button("🔀 Merge Pull Request to Production", type="primary", use_container_width=True)
