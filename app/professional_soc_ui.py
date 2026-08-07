import json
import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = PROJECT_ROOT / "agents"
for candidate in [str(PROJECT_ROOT), str(AGENTS_DIR)]:
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from soc_agent_orchestrator import SOCAgentOrchestrator


st.set_page_config(
    page_title="SOC Operations Console",
    page_icon="",
    layout="wide",
)


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0f172a;
                --panel: #111827;
                --panel-soft: #1f2937;
                --line: #334155;
                --text: #e5e7eb;
                --muted: #94a3b8;
                --primary: #60a5fa;
                --success: #34d399;
                --warning: #fbbf24;
                --danger: #f87171;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background: #020817;
                color: var(--text);
            }

            .stApp {
                background: linear-gradient(180deg, #020817 0%, #0f172a 100%);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            div[data-testid="stSidebar"] {
                background: #0b1220;
                border-right: 1px solid var(--line);
            }

            .stMetric {
                background: rgba(17, 24, 39, 0.85);
                border: 1px solid var(--line);
                border-radius: 10px;
                padding: 0.75rem;
            }

            .stAlert {
                border-radius: 10px;
            }

            .stTabs [role="tablist"] {
                gap: 0.5rem;
            }

            .stTabs [role="tab"] {
                background: #111827;
                border: 1px solid var(--line);
                border-radius: 8px 8px 0 0;
            }
            .stTabs [role="tab"][aria-selected="true"] {
                background: #1e293b;
                border-bottom: none;
            }

            .section-box {
                background: rgba(17, 24, 39, 0.9);
                border: 1px solid var(--line);
                border-radius: 12px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_styles()


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
            "compute": {"instances": [{"name": "web-server", "public_ip": False, "ssh_open": False, "imdsv2_disabled": True}]},
        },
        "controls": {
            "access_control": {"mfa_required": True, "least_privilege": True, "inactive_accounts": False},
            "logging": {"centralized_logging": True, "retention_days": 120, "privileged_event_monitoring": True},
            "asset_management": {"inventory_complete": True, "owner_assigned": True},
            "vulnerability_management": {"patching_compliant": True, "vulnerability_scan_frequency_days": 7},
            "incident_response": {"playbooks_defined": True, "testing_exercised": True},
            "data_protection": {"encryption_at_rest": True, "backup_verified": True},
        },
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
            "compute": {"instances": [{"name": "db-host", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]},
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 20, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        },
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
            "compute": {"instances": [{"name": "exposed-vm", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]},
        },
        "controls": {
            "access_control": {"mfa_required": False, "least_privilege": False, "inactive_accounts": True},
            "logging": {"centralized_logging": False, "retention_days": 10, "privileged_event_monitoring": False},
            "asset_management": {"inventory_complete": False, "owner_assigned": False},
            "vulnerability_management": {"patching_compliant": False, "vulnerability_scan_frequency_days": 30},
            "incident_response": {"playbooks_defined": False, "testing_exercised": False},
            "data_protection": {"encryption_at_rest": False, "backup_verified": False},
        },
    },
    "normal monitoring": {
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
            "compute": {"instances": [{"name": "app-server", "public_ip": False, "ssh_open": False, "imdsv2_disabled": True}]},
        },
        "controls": {
            "access_control": {"mfa_required": True, "least_privilege": True, "inactive_accounts": False},
            "logging": {"centralized_logging": True, "retention_days": 180, "privileged_event_monitoring": True},
            "asset_management": {"inventory_complete": True, "owner_assigned": True},
            "vulnerability_management": {"patching_compliant": True, "vulnerability_scan_frequency_days": 7},
            "incident_response": {"playbooks_defined": True, "testing_exercised": True},
            "data_protection": {"encryption_at_rest": True, "backup_verified": True},
        },
    },
}


sample_path = PROJECT_ROOT / "samples" / "sample_incident.json"
if sample_path.exists():
    with sample_path.open("r", encoding="utf-8") as file:
        default_incident = json.load(file)
else:
    default_incident = THREAT_SCENARIOS["ransomware"]


def get_case_summary(result):
    decision = result.get("decision", "monitor")
    step = result.get("recommended_next_step", "continue_monitoring_and_collect_more_evidence")
    specialists = result.get("specialists", {})
    active = [name for name, payload in specialists.items() if isinstance(payload, dict)]

    summary = {
        "decision": decision,
        "next_step": step,
        "specialists_run": len(active),
        "agent_count": len(active),
    }
    return summary


def show_live_operation_log(incident, case_id, analyst):
    steps = [
        "Collecting telemetry from endpoint, identity, and network sources",
        "Analyzing malicious indicators and threat intelligence enrichment",
        "Reviewing cloud posture and privilege configuration",
        "Assessing compliance drift and policy violations",
        "Correlating log activity and user behavior anomalies",
        "Identifying the active attack path and blast radius",
        "Blocking suspicious network connections and isolating affected assets",
        "Revoking risky credentials and enforcing tighter access controls",
        "Triggering incident response workflow and escalation actions",
        "Threat neutralization completed; monitoring the environment for recurrence",
    ]

    log_container = st.container()
    with log_container:
        st.subheader("Live operations log")
        log_box = st.empty()

    messages = []
    for index, step in enumerate(steps, start=1):
        timestamp = time.strftime("%H:%M:%S")
        messages.append(f"[{timestamp}] {index}. {step}")
        log_box.code("\n".join(messages), language="text")
        time.sleep(0.7)

    final_status = {
        "case_id": case_id,
        "analyst": analyst,
        "incident_type": incident.get("case_id", "unknown"),
        "status": "Threat containment workflow completed",
        "summary": "The AI has evaluated the threat, correlated evidence, and executed containment actions.",
    }
    log_box.code(json.dumps(final_status, indent=2), language="json")


with st.sidebar:
    st.header("Incident Control")
    scenario_name = st.selectbox("Threat scenario", list(THREAT_SCENARIOS.keys()))
    if st.button("Load scenario"):
        st.session_state["incident_json"] = json.dumps(THREAT_SCENARIOS[scenario_name], indent=2)
        st.session_state["case_id"] = THREAT_SCENARIOS[scenario_name].get("case_id", "SOC-900")
        st.session_state["analyst"] = THREAT_SCENARIOS[scenario_name].get("analyst", "SOC Analyst")

    case_id = st.text_input("Case ID", value=st.session_state.get("case_id", default_incident.get("case_id", "SOC-900")))
    analyst = st.text_input("Analyst", value=st.session_state.get("analyst", default_incident.get("analyst", "SOC Analyst")))
    incident_json = st.text_area(
        "Incident JSON",
        value=st.session_state.get("incident_json", json.dumps(default_incident, indent=2)),
        height=360,
    )
    run_button = st.button("Run workflow", type="primary")


st.title("SOC Operations Console")
st.caption("Security operations multi-agent workflow for detection, triage, and response coordination.")

if run_button:
    try:
        incident = json.loads(incident_json)
        incident["case_id"] = case_id
        incident["analyst"] = analyst

        orchestrator = SOCAgentOrchestrator(case_id=case_id, analyst=analyst)
        result = orchestrator.run_incident(incident)
        summary = get_case_summary(result)

        st.success(f"Decision: {summary['decision']} | Next step: {summary['next_step']}")

        show_live_operation_log(incident, case_id, analyst)

        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Decision", summary["decision"])
        with metric_cols[1]:
            st.metric("Next step", summary["next_step"])
        with metric_cols[2]:
            st.metric("Specialists", summary["specialists_run"])
        with metric_cols[3]:
            st.metric("Case ID", case_id)

        overview = st.container()
        with overview:
            st.markdown("<div class='section-box'><h3>Case Summary</h3></div>", unsafe_allow_html=True)
            summary_text = result.get("specialists", {})
            if summary_text:
                st.write(
                    "This case was reviewed across the specialist agent set and combined into a single operational recommendation."
                )
            else:
                st.write("No specialist data was provided for this case.")

        col_left, col_right = st.columns([1.6, 1])
        with col_left:
            st.subheader("Specialist Findings")
            for name, payload in result.get("specialists", {}).items():
                with st.expander(name.replace("_", " ").title(), expanded=True):
                    st.json(payload)

        with col_right:
            st.subheader("Response Plan")
            st.markdown(
                f"""
                <div class='section-box'>
                    <p><strong>Decision:</strong> {summary['decision']}</p>
                    <p><strong>Recommended next step:</strong> {summary['next_step']}</p>
                    <p><strong>Analyst:</strong> {analyst}</p>
                    <p><strong>Case ID:</strong> {case_id}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("Incident Overview")
            st.json({
                "case_id": case_id,
                "analyst": analyst,
                "events": len(incident.get("logs", [])),
                "observables": len(incident.get("observables", [])),
                "cloud_config": bool(incident.get("cloud_config")),
                "controls": bool(incident.get("controls")),
            })

        with st.expander("Full Orchestrator Output", expanded=False):
            st.json(result)

    except Exception as exc:
        st.error(f"Workflow failed: {exc}")
else:
    st.info("Select a scenario or update the incident payload, then run the workflow to review the SOC decision and specialist findings.")
    st.markdown(
        """
        <div class='section-box'>
            <h3>Overview</h3>
            <p>This console provides a structured view of SOC incident analysis across malware, cloud security, compliance, threat intelligence, and log analytics.</p>
            <p>The workflow evaluates the incident, assigns a decision, and proposes the next response action for the analyst.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    default_result = {
        "decision": "monitor",
        "recommended_next_step": "continue_monitoring_and_collect_more_evidence",
        "specialists": {
            "log_analysis": {"status": "ready"},
            "cloud_security": {"status": "ready"},
            "compliance_analysis": {"status": "ready"},
            "threat_intelligence": {"status": "ready"},
        },
    }

    st.json(default_result)
