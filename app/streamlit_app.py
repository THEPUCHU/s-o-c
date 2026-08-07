import streamlit as st
import time
import sys
import os
import pandas as pd
from pathlib import Path

# --- BULLETPROOF PATH ROUTING ---
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from agents.soc_agent_orchestrator import SOCAgentOrchestrator
except ImportError:
    pass # Fails gracefully so UI still renders for the demo

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SOC Intelligence",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BLACK & ORANGE CSS ---
st.markdown("""
    <style>
    /* Main Background & Global Text */
    .stApp { background-color: #050505; color: #eaeaea; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #0d0d0d; 
        border-right: 2px solid #ff6600; 
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 { 
        color: #ff8c00 !important; 
        font-weight: 600; 
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #333333;
        border-top: 3px solid #ff6600;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(255, 102, 0, 0.15);
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #ff8c00 !important; }
    
    /* Dividers */
    hr { 
        border-top: 2px solid #ff6600 !important; 
        opacity: 0.3; 
    }
    
    /* Primary Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #ff6600 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #ff8c00 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #e65c00 !important;
        color: #ffffff !important;
        border: 1px solid #ff6600 !important;
    }
    
    /* Dataframes/Tables */
    .stDataFrame { border: 1px solid #ff6600; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown("## 🔥")
with col_title:
    st.title("Enterprise SOC Intelligence Platform")
    st.caption("Autonomous Agentic Threat Resolution & Policy Enforcement")

st.divider()

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.subheader("⚙️ Agent Configuration")
    ai_model = st.selectbox("LLM Reasoning Engine", ["GPT-4o (Primary)", "Claude-3.5-Sonnet (Fallback)", "Llama-3 (Local/Fast)"])
    st.slider("Agent Confidence Threshold (%)", min_value=50, max_value=99, value=85)
    
    st.divider()
    st.subheader("📥 Ingestion Queue")
    selected_incident = st.radio(
        "Select Pending Alert:",
        ["🚨 INC-9942: Data Exfiltration", "⚠️ INC-9943: Multi-Region Login", "🛡️ INC-9944: Misconfigured S3"]
    )
    
    run_workflow = st.button("▶ Initialize Agent Swarm", type="primary", use_container_width=True)

# --- MAIN DASHBOARD (PRE-RUN) ---
if not run_workflow:
    st.info("Awaiting command. Select an incident from the queue and initialize the swarm.")
    
    # Mock data table for the empty state
    st.subheader("Global Threat Feed")
    df = pd.DataFrame({
        "Severity": ["High", "Medium", "Low", "Critical"],
        "Source": ["AWS CloudTrail", "Okta IAM", "CrowdStrike", "Palo Alto Firewall"],
        "Event": ["Bucket Policy Altered", "Failed MFA", "Malware Quarantined", "C2 Traffic Blocked"],
        "Status": ["Pending triage", "Pending triage", "Resolved", "Pending triage"]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- MAIN DASHBOARD (POST-RUN) ---
if run_workflow:
    # 1. LIVE AGENT STATUS TRACKER
    st.subheader("🔄 Multi-Agent Workflow Execution")
    
    with st.status("Deploying SOC Agents...", expanded=True) as status:
        st.write("📡 Ingesting raw telemetry...")
        time.sleep(0.5)
        st.write("🧠 SOC Coordinator decomposing tasks...")
        time.sleep(0.8)
        st.write("🔍 Threat Intel Agent querying external databases...")
        time.sleep(0.8)
        st.write("📊 Log Analysis Agent correlating internal timestamps...")
        time.sleep(1)
        st.write("⚖️ Incident Response Agent finalizing containment plan...")
        time.sleep(0.5)
        status.update(label="Incident Analyzed Successfully", state="complete", expanded=False)

    st.divider()

    # 2. KEY METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Incident Classification", value="True Positive")
    with m2:
        st.metric(label="Primary Attacker IP", value="103.45.9.112", delta="Flagged by 4 vendors", delta_color="inverse")
    with m3:
        st.metric(label="MITRE Tactic", value="T1048", delta="Exfiltration")
    with m4:
        st.metric(label="Recommended Action", value="Isolate Host")

    # 3. DETAILED REPORTS (SPLIT LAYOUT)
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📋 Executive Summary")
        st.warning("**Root Cause:** A compromised IAM role (`dev-ops-admin`) was utilized to alter an S3 bucket policy, exposing sensitive data to the public internet.")
        
        st.markdown("### 🛡️ Autonomous Containment Plan")
        action_df = pd.DataFrame({
            "Step": [1, 2, 3],
            "Action": ["Revoke active AWS sessions for `dev-ops-admin`", "Revert S3 Bucket policy to previous known-good state", "Block IP `103.45.9.112` at WAF"],
            "Agent Owner": ["Cloud Security Agent", "Compliance Agent", "Incident Response Agent"]
        })
        st.data_editor(action_df, hide_index=True, disabled=True, use_container_width=True)
        
        st.button("✅ Approve & Execute Containment Playbook", type="primary")

    with col_right:
        st.markdown("### 🔍 Agent Explainability Logs")
        with st.expander("Threat Intelligence Agent Data", expanded=True):
            st.json({
                "query_target": "103.45.9.112",
                "virustotal_score": "14/94",
                "abuseipdb_confidence": "89%",
                "known_aliases": ["FIN7", "Carbanak"]
            })
        with st.expander("Cloud Security Agent Data"):
            st.code("""
            {
              "EventName": "PutBucketPolicy",
              "UserIdentity": {
                "type": "IAMUser",
                "principalId": "AIDAJ45Q7Y6EZGEXAMPLE",
                "userName": "dev-ops-admin"
              }
            }
            """, language="json")
