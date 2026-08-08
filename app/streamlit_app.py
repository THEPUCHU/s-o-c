import streamlit as st
import time
import sys
import os
import pandas as pd
from pathlib import Path

# --- BULLETPROOF PATH ROUTING ---
# This tells the 'app' folder to look up one level to find the 'agents' folder
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now this import will work flawlessly
try:
    from agents.soc_agent_orchestrator import SOCAgentOrchestrator
    backend_connected = True
except ImportError as e:
    backend_connected = False
    st.error(f"Backend Connection Error: {e}")

# --- PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="SOC Intelligence", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #eaeaea; }
    [data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 2px solid #ff6600; }
    h1, h2, h3, h4 { color: #ff8c00 !important; font-weight: 600; }
    [data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-top: 3px solid #ff6600; padding: 15px; border-radius: 8px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #ff8c00 !important; }
    hr { border-top: 2px solid #ff6600 !important; opacity: 0.3; }
    div.stButton > button[kind="primary"] { background-color: #ff6600 !important; color: #000000 !important; font-weight: bold !important; border: 1px solid #ff8c00 !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🔥 Enterprise SOC Intelligence Platform")
st.caption("Live Autonomous Agentic Threat Resolution powered by Groq")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ Configuration")
    ai_model = st.selectbox("LLM Engine", ["Groq Llama-3"])
    target_ip = st.text_input("Enter Target IP:", value="198.51.100.45")
    run_workflow = st.button("▶ Initialize Swarm", type="primary", use_container_width=True)

# --- DASHBOARD LOGIC ---
if run_workflow and backend_connected:
    st.subheader("🔄 Multi-Agent Workflow Execution")
    
    with st.status("Deploying SOC Agents...", expanded=True) as status:
        # Initialize orchestrator
        orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE", analyst="System")
        
        # Build payload
        live_incident = {
            "observables": [{"value": target_ip, "type": "ip", "severity": "high"}]
        }
        
        # Run it!
        st.write(f"📡 Agents investigating target: {target_ip}...")
        final_results = orchestrator.run_incident(live_incident)
        status.update(label="Analysis Complete", state="complete", expanded=False)

    st.divider()
    
    st.subheader("📊 Live Intelligence Output")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🛡️ Swarm Decision")
        st.warning(f"**Recommendation:** {final_results.get('recommended_next_step', 'Unknown').replace('_', ' ').title()}")
        st.button("✅ Execute Playbook", type="primary")

    with col2:
        st.markdown("### 🔍 Real Agent Outputs")
        for agent_name, agent_data in final_results.get("specialists", {}).items():
            if isinstance(agent_data, dict) and agent_name != "status":
                with st.expander(f"{agent_name.replace('_', ' ').title()} Report"):
                    st.json(agent_data)
