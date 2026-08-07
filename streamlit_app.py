import json
from pathlib import Path

import streamlit as st

from soc_agent_orchestrator import SOCAgentOrchestrator


st.set_page_config(page_title="SOC Agent Orchestrator", page_icon="🛡️", layout="wide")

st.title("SOC Agent Workflow Dashboard")
st.caption("Multi-agent security operations workflow for malware, cloud, compliance, threat intel, and log analysis")

sample_path = Path("samples/sample_incident.json")

if sample_path.exists():
    with sample_path.open("r", encoding="utf-8") as f:
        default_incident = json.load(f)
else:
    default_incident = {
        "case_id": "SOC-900",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T10:00:00Z event=LoginFailed user=admin src=10.0.0.10",
            "2026-08-08T10:05:00Z event=PowerShell execution user=svc_admin src=10.0.0.20",
        ],
        "observables": [
            {"value": "198.51.100.10", "type": "ip", "severity": "high"},
            {"value": "malware.example", "type": "domain", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {"root_user_enabled": True, "policies": [{"name": "admin-policy", "statements": [{"effect": "Allow", "action": "*", "resource": "*"}]}]},
            "storage": {"buckets": [{"name": "public-bucket", "public_access": True, "encryption": "disabled"}]},
            "network": {"security_groups": [{"name": "web-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "22"}]}]},
            "logging": {"cloudtrail_enabled": False, "guardduty_enabled": False},
            "secrets": {"values": [{"name": "db-pass", "hardcoded": True}]},
            "compute": {"instances": [{"name": "public-host", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]}
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 20, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        },
    }

with st.sidebar:
    st.header("Incident settings")
    case_id = st.text_input("Case ID", value=default_incident.get("case_id", "SOC-900"))
    analyst = st.text_input("Analyst", value=default_incident.get("analyst", "SOC Analyst"))
    st.text("Use the sample payload or paste a custom JSON incident below.")
    incident_json = st.text_area("Incident JSON", value=json.dumps(default_incident, indent=2), height=300)

    run_button = st.button("Run workflow", type="primary")

if run_button:
    try:
        incident = json.loads(incident_json)
        incident["case_id"] = case_id
        incident["analyst"] = analyst

        orchestrator = SOCAgentOrchestrator(case_id=case_id, analyst=analyst)
        result = orchestrator.run_incident(incident)

        st.success(f"Decision: {result.get('decision')} | Next Step: {result.get('recommended_next_step')}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Decision", result.get("decision", "unknown"))
        with col2:
            st.metric("Recommended step", result.get("recommended_next_step", "unknown"))
        with col3:
            st.metric("Specialists run", str(len(result.get("specialists", {}))))

        for name, payload in result.get("specialists", {}).items():
            with st.expander(f"{name}", expanded=True):
                st.json(payload)

        with st.expander("Full orchestrator output", expanded=False):
            st.json(result)

    except Exception as exc:
        st.error(f"Workflow failed: {exc}")
else:
    st.info("Load the sample incident, edit it if needed, and click 'Run workflow' to observe the SOC agent orchestration.")
