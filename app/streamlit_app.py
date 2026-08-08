import streamlit as st
import sys
import time
import random
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

# --- PAGE CONFIGURATION & DESIGN SYSTEM ---
st.set_page_config(page_title="Autonomous SOC AI", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg: #08090b;
        --bg-elevated: #101216;
        --bg-card: #14161b;
        --border: #23262e;
        --accent: #ff6a1a;
        --accent-soft: #ff6a1a22;
        --accent-glow: #ff6a1a55;
        --text-primary: #f2f2f0;
        --text-muted: #8b8f98;
        --blue: #4f8cff;
        --purple: #a970ff;
        --green: #2fd18f;
        --red: #ff5470;
    }

    html, body { font-family: 'Inter', sans-serif; }
    .stApp { background-color: var(--bg); color: var(--text-primary); font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: var(--bg-elevated); border-right: 1px solid var(--border); }

    /* Apply Inter to sidebar text but exclude icon-font elements (Material Symbols),
       otherwise the collapse-arrow icon renders as literal text like "keyboard_double_arrow_left" */
    [data-testid="stSidebar"] :not([data-testid="stIconMaterial"]):not([class*="material"]) {
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stIconMaterial"], span[class*="material-symbols"], [data-testid="baseButton-headerNoPadding"] * {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }

    h1, h2, h3, h4, h5 { color: var(--text-primary) !important; font-weight: 700; letter-spacing: -0.01em; }
    p, span, label, .stMarkdown { color: var(--text-primary); }
    hr { border-top: 1px solid var(--border) !important; opacity: 1; margin: 1.1rem 0; }

    /* Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff6a1a, #ff8c3a) !important;
        color: #0a0a0a !important; font-weight: 700 !important; border: none !important;
        border-radius: 10px !important; padding: 0.6rem 1rem !important;
        box-shadow: 0 4px 18px var(--accent-glow) !important; transition: transform 0.15s ease !important;
    }
    div.stButton > button[kind="primary"]:hover { transform: translateY(-1px); }

    /* ===== Header: icon + title on ONE line, status pill inline ===== */
    .app-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px; }
    .app-header-left { display: flex; align-items: center; gap: 12px; }
    .app-header-left .flame { font-size: 30px; line-height: 1; filter: drop-shadow(0 0 10px var(--accent-glow)); }
    .app-header-left h1 { font-size: 26px; margin: 0; line-height: 1; }
    .status-pill {
        display: inline-flex; align-items: center; gap: 7px; background: #0f2318; border: 1px solid #1f4a34;
        color: var(--green); font-size: 12.5px; font-weight: 600; padding: 6px 12px; border-radius: 999px;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 1.8s infinite; }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
    .app-subtitle { color: var(--text-muted); font-size: 13.5px; margin-top: 2px; margin-bottom: 18px; }

    /* Section labels */
    .section-label { color: var(--text-muted); font-size: 11.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; }

    /* Agent cards */
    .agent-card {
        border-radius: 12px; padding: 14px 10px; text-align: center; border: 1px solid var(--border);
        background: var(--bg-card); transition: all 0.25s ease; position: relative;
    }
    .agent-card .icon { font-size: 24px; margin-bottom: 8px; }
    .agent-card .name { font-size: 13px; font-weight: 600; margin: 0; }
    .agent-card .status { font-size: 11px; margin-top: 4px; font-weight: 500; }
    .agent-card.master { padding: 16px 12px; }

    .connector { text-align: center; color: var(--border); font-size: 18px; margin: 2px 0 8px 0; }

    /* Terminal Log */
    .action-log {
        font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ffb37a; background: #0a0b0d;
        padding: 16px; border-radius: 10px; border: 1px solid var(--border); border-left: 3px solid var(--accent);
        line-height: 1.75;
    }
    .success-text { color: var(--green); font-weight: 600; }
    .alert-text { color: var(--red); font-weight: 700; }

    /* Attack Chain Visualization */
    .attack-node {
        background: var(--bg-card); border: 1px solid var(--border); border-left: 3px solid var(--red);
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
    }
    .attack-node .title { color: var(--red); font-weight: 700; font-size: 13.5px; }
    .attack-node .sub { color: var(--text-muted); font-size: 12.5px; margin-top: 2px; }
    .arrow { text-align: center; color: var(--border); font-size: 16px; margin-bottom: 8px; }

    /* Metric cards (custom, replacing default st.metric look) */
    .metric-card {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
        padding: 14px 16px;
    }
    .metric-card .m-label { color: var(--text-muted); font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .m-value { font-size: 20px; font-weight: 700; margin-top: 4px; }
    .metric-card .m-delta { font-size: 12px; color: var(--accent); margin-top: 2px; }

    [data-testid="stMetricValue"] { color: var(--text-primary); }
    [data-testid="stMetricDelta"] { color: var(--accent) !important; }

    .stAlert { border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)


def render_agent_card(agent_name, icon, state, is_master=False):
    if state == "idle":
        border, text, status = "#23262e", "#5c6170", "Standby"
    elif state == "running":
        border, text, status = "#ff6a1a", "#ff8c3a", "Processing…"
    elif state == "routing":
        border, text, status = "#4f8cff", "#79a6ff", "Routing tasks…"
    elif state == "consensus":
        border, text, status = "#a970ff", "#c49bff", "Computing consensus…"
    else:
        border, text, status = "#2fd18f", "#4fe0a5", "Deployed"

    glow = f"box-shadow: 0 0 22px {border}30;" if state != "idle" else ""
    master_class = "master" if is_master else ""

    return f"""
    <div class="agent-card {master_class}" style="border-color: {border}; {glow}">
        <div class="icon">{icon}</div>
        <p class="name" style="color: {text};">{agent_name}</p>
        <div class="status" style="color: {text};">{status}</div>
    </div>
    """


def metric_card(label, value, delta=""):
    delta_html = f'<div class="m-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="m-label">{label}</div>
        <div class="m-value">{value}</div>
        {delta_html}
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
    },
    "DDoS Volumetric Attack": {
        "ip": "185.220.101.7",
        "file": "N/A (Network Layer Attack)",
        "cloud_env": "AWS (CloudFront / ELB Target)",
        "logs": ["2026-08-08 Traffic spike 400Gbps detected", "2026-08-08 SYN flood from botnet cluster"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "actions": "> Enabling Scrubbing Center Redirect... <span class='success-text'>SUCCESS</span><br>> Blackholing Botnet Source Ranges... <span class='success-text'>SUCCESS</span><br>> Scaling Edge Capacity +300%... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Botnet Cluster<br>10,000+ Nodes", "Volumetric Flood<br>400Gbps SYN", "Edge Saturation<br>ELB / CloudFront"]
    },
    "Supply Chain Compromise": {
        "ip": "45.33.12.190",
        "file": "C:\\Program Files\\VendorApp\\update_pkg.dll",
        "cloud_env": "Azure (CI/CD Pipeline Target)",
        "logs": ["2026-08-08 Unsigned DLL injected via vendor update", "2026-08-08 Anomalous outbound traffic post-update"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "actions": "> Halting CI/CD Deployment Pipeline... <span class='success-text'>SUCCESS</span><br>> Rolling Back Vendor Package... <span class='success-text'>SUCCESS</span><br>> Quarantining update_pkg.dll... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Compromised Vendor<br>Update Channel", "Malicious DLL<br>update_pkg.dll", "Pipeline Injection<br>CI/CD System"]
    },
    "Zero-Day Exploit (Web App)": {
        "ip": "91.219.237.14",
        "file": "/var/www/html/shell_backdoor.php",
        "cloud_env": "GCP (App Engine / Public Bucket)",
        "logs": ["2026-08-08 Anomalous WAF bypass detected", "2026-08-08 Webshell dropped via unpatched CVE"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 1}},
        "actions": "> Deploying Virtual Patch to WAF... <span class='success-text'>SUCCESS</span><br>> Removing Webshell shell_backdoor.php... <span class='success-text'>SUCCESS</span><br>> Isolating App Engine Instance... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Unpatched CVE<br>Web Application", "Webshell Drop<br>shell_backdoor.php", "Remote Code Exec<br>App Engine Instance"]
    },
    "Executive Phishing (BEC)": {
        "ip": "77.88.55.203",
        "file": "N/A (Social Engineering / Email)",
        "cloud_env": "Microsoft 365 (Mailbox Compromise)",
        "logs": ["2026-08-08 Impossible travel login for CFO account", "2026-08-08 Wire transfer request sent from mailbox rule"],
        "config": {"iam": {"root_user_enabled": False}, "storage": {"public_buckets": 0}},
        "actions": "> Forcing Password Reset + MFA Re-enrollment... <span class='success-text'>SUCCESS</span><br>> Removing Malicious Mailbox Forwarding Rule... <span class='success-text'>SUCCESS</span><br>> Freezing Pending Wire Transfer... <span class='success-text'>SUCCESS</span>",
        "nodes": ["Credential Phish<br>CFO Mailbox", "Malicious Mail Rule<br>Auto-Forwarding", "Fraudulent Wire<br>Transfer Request"]
    }
}

# --- DIFFICULTY SETTINGS (controls agent animation pacing) ---
# Each agent's "thinking time" is randomized within this range (seconds),
# and the order in which specialist agents finish is shuffled each run.
difficulty_settings = {
    "Easy":      {"range": (0.05, 0.25), "desc": "Fast pass — agents react almost instantly."},
    "Medium":    {"range": (0.20, 0.65), "desc": "Standard pace — realistic analysis time."},
    "Hard":      {"range": (0.50, 1.30), "desc": "Deliberate — agents take longer to correlate signals."},
    "Nightmare": {"range": (1.00, 2.40), "desc": "Slow burn — every stage lingers under pressure."},
}


def fmt_duration(seconds):
    """Format a duration in ms if under a second, otherwise in seconds."""
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    return f"{seconds:.2f} s"


# --- HEADER: icon + title on one line, status pill on the right ---
st.markdown("""
<div class="app-header">
    <div class="app-header-left">
        <span class="flame">🔥</span><h1>Autonomous SOC AI</h1>
    </div>
    <div class="status-pill"><span class="status-dot"></span>ENGINE ONLINE</div>
</div>
<div class="app-subtitle">Self-directing agentic swarm · zero-latency threat neutralization</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="section-label">Threat Scenario</div>', unsafe_allow_html=True)
    selected_scenario = st.selectbox("Select Threat Scenario:", list(scenarios.keys()), label_visibility="collapsed")
    s_data = scenarios[selected_scenario]

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Response Difficulty</div>', unsafe_allow_html=True)
    selected_difficulty = st.select_slider(
        "Response Difficulty:",
        options=list(difficulty_settings.keys()),
        value="Medium",
        label_visibility="collapsed"
    )
    st.caption(difficulty_settings[selected_difficulty]["desc"])
    delay_min, delay_max = difficulty_settings[selected_difficulty]["range"]

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    run_workflow = st.button("▶  Execute Agentic Response", type="primary", use_container_width=True)

# --- NEURAL SWARM TRACKER ---
st.markdown('<div class="section-label">Neural Swarm Activity</div>', unsafe_allow_html=True)

col_spacer1, col_orch, col_spacer2 = st.columns([1.8, 1.4, 1.8])
ui_orchestrator = col_orch.empty()
ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "idle", is_master=True), unsafe_allow_html=True)

st.markdown("<div class='connector'>▾</div>", unsafe_allow_html=True)

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
    st.markdown('<div class="section-label">Environment Readiness</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric_card("Monitored Endpoints", "12,402", "Online"), unsafe_allow_html=True)
    m2.markdown(metric_card("Cloud Assets", "843", "AWS · GCP · Azure"), unsafe_allow_html=True)
    m3.markdown(metric_card("Active Policies", "142", "NIST-800-53"), unsafe_allow_html=True)
    m4.markdown(metric_card("Swarm Latency", "12 ms", "Optimal"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Pending Injection Payload</div>', unsafe_allow_html=True)
    st.info(f"Targeting **{selected_scenario}** · Difficulty **{selected_difficulty}**. The Orchestrator will ingest this data upon deployment.")

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
    agent_durations = {}

    op_start = time.time()

    # Specialist agent pool — order randomized each run so agents finish in a
    # different sequence every time, and each gets its own random "think time".
    agent_pool = [
        {
            "key": "threat_intelligence",
            "name": "Threat Intel",
            "icon": "🌐",
            "ui": ui_intel,
            "run": lambda: orchestrator._run_threat_intel(live_incident["observables"]),
        },
        {
            "key": "log_analysis",
            "name": "Log Analysis",
            "icon": "📜",
            "ui": ui_log,
            "run": lambda: orchestrator._run_log_analysis(live_incident["logs"]),
        },
        {
            "key": "malware_analysis",
            "name": "Malware AI",
            "icon": "🦠",
            "ui": ui_malware,
            "run": lambda: orchestrator._run_malware(live_incident["file_path"]),
        },
        {
            "key": "cloud_security",
            "name": "Cloud Sec",
            "icon": "☁️",
            "ui": ui_cloud,
            "run": lambda: orchestrator._run_cloud_security(live_incident["cloud_config"]),
        },
        {
            "key": "compliance_analysis",
            "name": "Compliance",
            "icon": "📋",
            "ui": ui_comp,
            "run": lambda: orchestrator._run_compliance(live_incident["controls"]),
        },
    ]
    random.shuffle(agent_pool)

    with st.spinner("Master Orchestrator has taken control..."):

        # Step 1: Orchestrator Ingests & Routes
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "routing", is_master=True), unsafe_allow_html=True)
        time.sleep(random.uniform(delay_min, delay_max))

        # Step 2: Agents execute in randomized order, each with its own random delay
        for agent in agent_pool:
            agent["ui"].markdown(render_agent_card(agent["name"], agent["icon"], "running"), unsafe_allow_html=True)
            agent_start = time.time()
            time.sleep(random.uniform(delay_min, delay_max))
            final_results["specialists"][agent["key"]] = agent["run"]()
            agent_durations[agent["key"]] = time.time() - agent_start
            agent["ui"].markdown(render_agent_card(agent["name"], agent["icon"], "done"), unsafe_allow_html=True)

        # Step 3: Orchestrator re-takes control to decide final action
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "consensus", is_master=True), unsafe_allow_html=True)
        time.sleep(random.uniform(delay_min, delay_max))
        final_results["decision"] = orchestrator._decide_priority(final_results["specialists"])
        final_results["recommended_next_step"] = orchestrator._next_step(final_results["decision"])

        # Final Orchestrator completion
        ui_orchestrator.markdown(render_agent_card("Master Orchestrator", "🧠", "done", is_master=True), unsafe_allow_html=True)
        time.sleep(random.uniform(delay_min, delay_max))

    total_elapsed = time.time() - op_start
    finish_order = " → ".join(agent["name"] for agent in agent_pool)

    st.success(f"✅ {selected_scenario} neutralized autonomously by Orchestrator ({selected_difficulty} difficulty) — completed in {fmt_duration(total_elapsed)}")
    st.caption(f"🔀 Agent completion order this run: {finish_order}")

    t1, t2, t3 = st.columns(3)
    t1.markdown(metric_card("⏱ Total Response Time", fmt_duration(total_elapsed)), unsafe_allow_html=True)
    t2.markdown(metric_card(
        "🐢 Slowest Agent",
        max(agent_durations, key=agent_durations.get).replace("_", " ").title(),
        fmt_duration(max(agent_durations.values()))
    ), unsafe_allow_html=True)
    t3.markdown(metric_card(
        "⚡ Fastest Agent",
        min(agent_durations, key=agent_durations.get).replace("_", " ").title(),
        fmt_duration(min(agent_durations.values()))
    ), unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns([1.2, 1, 1.2])

    with col1:
        st.markdown('<div class="section-label">Orchestrator Execution Log</div>', unsafe_allow_html=True)
        action_decision = final_results.get('recommended_next_step', 'isolate_and_block').replace('_', ' ').upper()

        st.markdown(f"""
        <div class="action-log">
            [ORCHESTRATOR] Data payload parsed and routed.<br>
            [ORCHESTRATOR] Sub-agent telemetry received.<br>
            [ORCHESTRATOR] Cross-correlating findings...<br>
            [ORCHESTRATOR] Final consensus reached. Bypassing human approval.<br>
            <br>
            &gt; DEPLOYING PLAYBOOK: {action_decision}<br>
            {s_data["actions"]}<br>
            <br>
            [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-label">Visual Threat Topography</div>', unsafe_allow_html=True)
        nodes_html = ""
        for i, node in enumerate(s_data["nodes"]):
            title, sub = node.split("<br>")
            nodes_html += f'<div class="attack-node"><div class="title">{title}</div><div class="sub">{sub}</div></div>'
            if i < len(s_data["nodes"]) - 1:
                nodes_html += '<div class="arrow">↓</div>'
        st.markdown(nodes_html, unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="section-label">AI Explainability Data</div>', unsafe_allow_html=True)

        with st.expander("Master Orchestrator Final Decision", expanded=True):
            st.json({
                "computed_priority": final_results["decision"],
                "executed_action": action_decision,
                "agents_utilized": 5,
                "difficulty": selected_difficulty,
                "total_response_time": fmt_duration(total_elapsed),
                "agent_finish_order": [agent["name"] for agent in agent_pool]
            })

        for agent_name, agent_data in final_results.get("specialists", {}).items():
            if isinstance(agent_data, dict) and agent_name != "status":
                duration_label = fmt_duration(agent_durations.get(agent_name, 0))
                with st.expander(f"{agent_name.replace('_', ' ').title()} Output — {duration_label}"):
                    st.json(agent_data)
