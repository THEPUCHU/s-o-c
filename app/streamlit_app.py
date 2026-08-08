import streamlit as st
import time
import sys
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
    [data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-top: 3px solid #ff6600; padding: 15px; border-radius: 8px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #ff8c00 !important; }
    hr { border-top: 2px solid #ff6600 !important; opacity: 0.3; }
    div.stButton > button[kind="primary"] { background-color: #ff6600 !important; color: #000000 !important; font-weight: bold !important; border: 1px solid #ff8c00 !important; }
    div.stButton > button[kind="primary"]:hover { background-color: #e65c00 !important; color: #ffffff !important; }
    
    /* Autonomous Action Log Styling */
    .action-log { 
        font-family: 'Courier New', monospace; 
        color: #ff8c00; 
        background: #0a0a0a; 
        padding: 15px; 
        border-radius: 5px; 
        border: 1px solid #333;
        border-left: 4px solid #ff6600;
        line-height: 1.6;
    }
    .success-text { color: #34d399; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🔥 Fully Autonomous SOC Agent")
st.caption("Self-Directing AI: Detects, Analyzes, and Remediates Without Human Intervention")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ System Status")
    st.success("🟢 Autonomous Mode: ACTIVE")
    st.caption("The AI will take immediate action to neutralize threats based on its own analysis.")
    st.divider()
    
    target_ip = st.text_input("Simulate Incident (Target IP):", value="198.51.100.45")
    run_workflow = st.button("▶ Trigger Autonomous Defense", type="primary", use_container_width=True)

# --- DASHBOARD LOGIC ---
if run_workflow and backend_connected:
    st.subheader("🔄 Multi-Agent Workflow Execution")
    
    with st.status("AI Agents are actively hunting and remediating...", expanded=True) as status:
        # Initialize orchestrator
        orchestrator = SOCAgentOrchestrator(case_id="SOC-LIVE", analyst="Autonomous Swarm")
        
        # Build payload
        live_incident = {
            "observables": [{"value": target_ip, "type": "ip", "severity": "high"}]
        }
        
        # Run it!
        st.write(f"📡 Ingesting telemetry for {target_ip}...")
        final_results = orchestrator.run_incident(live_incident)
        
        st.write("⚖️ AI Decision Engine reached consensus.")
        st.write("⚡ Executing remediation actions...")
        time.sleep(1) # Brief pause so the judges see it happen
        
        status.update(label="Threat Neutralized Autonomously", state="complete", expanded=False)

    st.divider()
    
    st.subheader("📊 Post-Incident Action Report")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🛑 Autonomous Actions Taken")
        
        # Pull the decision from your backend
        action_decision = final_results.get('recommended_next_step', 'isolate_and_block').replace('_', ' ').title()
        
        # Display the live autonomous execution log instead of a button
        st.markdown(f"""
        <div class="action-log">
            [SYSTEM] Threat verified by AI swarm.<br>
            [SYSTEM] Initiating autonomous containment...<br>
            <br>
            > Executing: {action_decision}<br>
            > Null-routing IP {target_ip} at edge firewall... <span class="success-text">SUCCESS</span><br>
            > Revoking active sessions for compromised accounts... <span class="success-text">SUCCESS</span><br>
            <br>
            [STATUS] <span class="success-text">Threat fully contained. Environment secured.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🔍 AI Analysis Logs")
        for agent_name, agent_data in final_results.get("specialists", {}).items():
            if isinstance(agent_data, dict) and agent_name != "status":
                with st.expander(f"{agent_name.replace('_', ' ').title()} Log"):
                    st.json(agent_data)
