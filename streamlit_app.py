import sys
import os
import json
import sys
from pathlib import Path

import streamlit as st

# 1. Get the absolute path of the root directory (where streamlit_app.py lives)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Point to the folder where soc_agent_orchestrator.py is located
# (Change 'src' to '.' if it is NOT in a folder and is sitting right next to streamlit_app.py)
backend_dir = os.path.join(current_dir, 'src') 

# 3. Force Python to look in that directory
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 4. Now the import will work
from soc_agent_orchestrator import SOCAgentOrchestrator



st.set_page_config(page_title="SOC Agent Orchestrator", page_icon="🛡️", layout="wide")

st.title("SOC Agent Workflow Dashboard")
st.caption("Multi-agent security operations workflow for malware, cloud, compliance, threat intel, and log analysis")

sample_path = PROJECT_ROOT / "samples" / "sample_incident.json"

THREAT_SCENARIOS = {
    "credential stuffing": {
        "case_id": "SOC-1001",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T10:00:00Z event=LoginFailed user=admin src=10.0.0.10",
            "2026-08-08T10:02:00Z event=LoginFailed user=finance src=10.0.0.11",
            "2026-08-08T10:05:00Z event=LoginFailed user=hr src=10.0.0.12",
            "2026-08-08T10:08:00Z event=Suspicious MFA fatigue user=admin src=10.0.0.15",
        ],
        "observables": [
            {"value": "203.0.113.77", "type": "ip", "severity": "medium"},
            {"value": "evil-login.example", "type": "domain", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {"root_user_enabled": False, "policies": [{"name": "user-policy", "statements": [{"effect": "Allow", "action": "iam:ListUsers", "resource": "*"}]}]},
            "storage": {"buckets": [{"name": "finance-bucket", "public_access": False, "encryption": "enabled"}]},
            "network": {"security_groups": [{"name": "admin-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "443"}]}]},
            "logging": {"cloudtrail_enabled": True, "guardduty_enabled": True},
            "secrets": {"values": [{"name": "app-token", "hardcoded": False}]},
            "compute": {"instances": [{"name": "web-server", "public_ip": False, "ssh_open": False, "imdsv2_disabled": True}]}
        },
        "controls": {
            "access_control": {"mfa_required": True, "least_privilege": True, "inactive_accounts": False},
            "logging": {"centralized_logging": True, "retention_days": 120, "privileged_event_monitoring": True},
            "asset_management": {"inventory_complete": True, "owner_assigned": True},
            "vulnerability_management": {"patching_compliant": True, "vulnerability_scan_frequency_days": 7},
            "incident_response": {"playbooks_defined": True, "testing_exercised": True},
            "data_protection": {"encryption_at_rest": True, "backup_verified": True},
        }
    },
    "ransomware": {
        "case_id": "SOC-2002",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T11:00:00Z event=PowerShell execution user=svc_admin src=10.0.0.20",
            "2026-08-08T11:02:00Z event=File encryption started user=svc_admin src=10.0.0.20",
            "2026-08-08T11:03:00Z event=ShadowCopy deletion user=svc_admin src=10.0.0.20",
            "2026-08-08T11:04:00Z event=Ransom note created user=svc_admin src=10.0.0.20",
        ],
        "observables": [
            {"value": "198.51.100.10", "type": "ip", "severity": "high"},
            {"value": "ransom.example", "type": "domain", "severity": "high"},
            {"value": "deadbeef", "type": "hash", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {"root_user_enabled": True, "policies": [{"name": "admin-policy", "statements": [{"effect": "Allow", "action": "*", "resource": "*"}]}]},
            "storage": {"buckets": [{"name": "backup-bucket", "public_access": True, "encryption": "disabled"}]},
            "network": {"security_groups": [{"name": "backup-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "3389"}]}]},
            "logging": {"cloudtrail_enabled": False, "guardduty_enabled": False},
            "secrets": {"values": [{"name": "admin-secret", "hardcoded": True}]},
            "compute": {"instances": [{"name": "db-host", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]}
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 20, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        }
    },
    "cloud exposure": {
        "case_id": "SOC-3003",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T12:00:00Z event=Bucket policy changed user=ops src=cloudapi",
            "2026-08-08T12:02:00Z event=Public access enabled user=ops src=cloudapi",
            "2026-08-08T12:04:00Z event=IAM key created user=ops src=cloudapi",
        ],
        "observables": [
            {"value": "198.51.100.44", "type": "ip", "severity": "high"},
            {"value": "cloud-breach.example", "type": "domain", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {"root_user_enabled": True, "policies": [{"name": "root-admin", "statements": [{"effect": "Allow", "action": "*", "resource": "*"}]}]},
            "storage": {"buckets": [{"name": "public-data", "public_access": True, "encryption": "disabled"}]},
            "network": {"security_groups": [{"name": "cloud-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "0"}]}]},
            "logging": {"cloudtrail_enabled": False, "guardduty_enabled": False},
            "secrets": {"values": [{"name": "access-key", "hardcoded": True}]},
            "compute": {"instances": [{"name": "exposed-vm", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]}
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 10, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        }
    },
    "normal / monitoring": {
        "case_id": "SOC-4004",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T13:00:00Z event=User login success user=analyst src=10.0.0.5",
            "2026-08-08T13:01:00Z event=API call success user=analyst src=10.0.0.5",
            "2026-08-08T13:02:00Z event=Report generated user=analyst src=10.0.0.5",
        ],
        "observables": [
            {"value": "10.0.0.5", "type": "ip", "severity": "low"},
            {"value": "internal.example", "type": "domain", "severity": "low"},
        ],
        "cloud_config": {
            "iam": {"root_user_enabled": False, "policies": [{"name": "standard-user", "statements": [{"effect": "Allow", "action": "s3:GetObject", "resource": "arn:aws:s3:::internal-bucket/*"}]}]},
            "storage": {"buckets": [{"name": "internal-bucket", "public_access": False, "encryption": "enabled"}]},
            "network": {"security_groups": [{"name": "internal-sg", "ingress": [{"cidr": "10.0.0.0/8", "port": "443"}]}]},
            "logging": {"cloudtrail_enabled": True, "guardduty_enabled": True},
            "secrets": {"values": [{"name": "internal-token", "hardcoded": False}]},
            "compute": {"instances": [{"name": "app-server", "public_ip": False, "ssh_open": False, "imdsv2_disabled": True}]}
        },
        "controls": {
            "access_control": {"mfa_required": True, "least_privilege": True, "inactive_accounts": False},
            "logging": {"centralized_logging": True, "retention_days": 180, "privileged_event_monitoring": True},
            "asset_management": {"inventory_complete": True, "owner_assigned": True},
            "vulnerability_management": {"patching_compliant": True, "vulnerability_scan_frequency_days": 7},
            "incident_response": {"playbooks_defined": True, "testing_exercised": True},
            "data_protection": {"encryption_at_rest": True, "backup_verified": True},
        }
    }
}

if sample_path.exists():
    with sample_path.open("r", encoding="utf-8") as f:
        default_incident = json.load(f)
else:
    default_incident = THREAT_SCENARIOS["ransomware"]

with st.sidebar:
    st.header("Incident settings")
    scenario_name = st.selectbox("Threat scenario", list(THREAT_SCENARIOS.keys()))
    if st.button("Load threat scenario"):
        default_incident = THREAT_SCENARIOS[scenario_name]
        st.session_state["incident_json"] = json.dumps(default_incident, indent=2)
        st.session_state["case_id"] = default_incident.get("case_id", "SOC-900")
        st.session_state["analyst"] = default_incident.get("analyst", "SOC Analyst")

    case_id = st.text_input("Case ID", value=st.session_state.get("case_id", default_incident.get("case_id", "SOC-900")))
    analyst = st.text_input("Analyst", value=st.session_state.get("analyst", default_incident.get("analyst", "SOC Analyst")))
    st.text("Use the sample payload or paste a custom JSON incident below.")
    incident_json = st.text_area("Incident JSON", value=st.session_state.get("incident_json", json.dumps(default_incident, indent=2)), height=300)

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
