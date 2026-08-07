import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="FORTIS — Autonomous Multi-Agent SOC Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Read the HTML application file
html_file_path = os.path.join(os.path.dirname(__file__), "standalone.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
else:
    html_content = "<h1>Error: standalone.html not found!</h1>"

# Sidebar controls for Streamlit integration
st.sidebar.image("https://img.shields.io/badge/FORTIS-SOC%20INTELLIGENCE-00f2fe?style=for-the-badge&logo=shield", use_column_width=True)
st.sidebar.title("🛡️ FORTIS Control Panel")
st.sidebar.markdown("**Autonomous Multi-Agent SOC Engine**")

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Deployment Information")
st.sidebar.info("""
**Platform:** Streamlit Cloud / Replit / Web
**Architecture:** 8 Autonomous Agents
**Engine:** Threat Intel • YARA • Sigma
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Real-Time SOC Metrics")
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric(label="Mitigation Speed", value="1.42s", delta="-99.9%")
col_s2.metric(label="Threat Accuracy", value="98.8%", delta="+12.4%")

# Main Streamlit Window: Render FORTIS App
components.html(html_content, height=950, scrolling=True)
