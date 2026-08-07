"""Run the SOC multi-agent workflow against the built-in sample incident."""

from __future__ import annotations

import json
from pathlib import Path

from soc_agent_orchestrator import SOCAgentOrchestrator


def main() -> int:
    incident = {
        "case_id": "SOC-900",
        "analyst": "SOC Analyst",
        "logs": [
            "2026-08-08T10:00:00Z event=LoginFailed user=admin src=10.0.0.10",
            "2026-08-08T10:05:00Z event=PowerShell execution user=svc_admin src=10.0.0.20",
            "2026-08-08T10:06:00Z event=RemoteDesktop login denied user=ops src=10.0.0.30",
        ],
        "observables": [
            {"value": "198.51.100.10", "type": "ip", "severity": "high"},
            {"value": "malware.example", "type": "domain", "severity": "high"},
            {"value": "abc123def456", "type": "hash", "severity": "high"},
        ],
        "cloud_config": {
            "iam": {
                "root_user_enabled": True,
                "policies": [{"name": "admin-policy", "statements": [{"effect": "Allow", "action": "*", "resource": "*"}]}],
            },
            "storage": {
                "buckets": [{"name": "public-bucket", "public_access": True, "encryption": "disabled"}],
            },
            "network": {
                "security_groups": [{"name": "web-sg", "ingress": [{"cidr": "0.0.0.0/0", "port": "22"}]}],
            },
            "logging": {"cloudtrail_enabled": False, "guardduty_enabled": False},
            "secrets": {"values": [{"name": "db-pass", "hardcoded": True}]},
            "compute": {
                "instances": [{"name": "public-host", "public_ip": True, "ssh_open": True, "imdsv2_disabled": False}]
            },
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

    orchestrator = SOCAgentOrchestrator(case_id=incident["case_id"], analyst=incident["analyst"])
    result = orchestrator.run_incident(incident)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
