"""SOC-focused cloud security analysis agent.

This module acts as a specialist security agent for cloud posture assessment.
It is designed to evaluate IAM, storage exposure, public access, insecure
configurations, and risky security settings in a structured way for SOC or IR
workflows.

Usage:
    python "cloud security.py" --cloud aws --config sample-config.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional


class CloudSecurityAgent:
    """Specialist agent for cloud security triage and posture assessment."""

    def __init__(self, cloud: str = "aws", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.cloud = cloud.lower()
        self.case_id = case_id
        self.analyst = analyst
        self.last_report: Dict[str, Any] = {}

    def analyze_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []

        findings.extend(self._check_iam(config.get("iam", {})))
        findings.extend(self._check_storage(config.get("storage", {})))
        findings.extend(self._check_network(config.get("network", {})))
        findings.extend(self._check_logging(config.get("logging", {})))
        findings.extend(self._check_secrets(config.get("secrets", {})))
        findings.extend(self._check_compute(config.get("compute", {})))

        severity = self._calculate_severity(findings)
        confidence = self._calculate_confidence(findings)
        risk_score = self._risk_score(findings)

        report = {
            "agent": "cloud_security",
            "case_id": self.case_id,
            "analyst": self.analyst,
            "cloud": self.cloud,
            "status": "completed",
            "summary": {
                "findings_count": len(findings),
                "severity": severity,
                "confidence": confidence,
                "risk_score": risk_score,
                "classification": self._classify(risk_score),
            },
            "findings": findings,
            "recommended_actions": self._recommended_actions(findings),
        }
        self.last_report = report
        return report

    def _check_iam(self, iam: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        policies = iam.get("policies", [])
        for policy in policies:
            name = policy.get("name", "unknown")
            statements = policy.get("statements", [])
            for statement in statements:
                effect = statement.get("effect", "Allow")
                action = statement.get("action", "")
                resource = statement.get("resource", "*")
                if effect.lower() == "allow" and ("*" in action or action == "*" or resource == "*"):
                    findings.append({
                        "category": "iam",
                        "severity": "high",
                        "title": "Overly permissive IAM policy",
                        "details": f"Policy {name} allows broad access: action={action}, resource={resource}",
                        "evidence": policy,
                    })

        if iam.get("root_user_enabled"):
            findings.append({
                "category": "iam",
                "severity": "high",
                "title": "Root account still enabled",
                "details": "Root or principal with unrestricted access remains enabled.",
                "evidence": iam,
            })
        return findings

    def _check_storage(self, storage: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        buckets = storage.get("buckets", [])
        for bucket in buckets:
            public = bucket.get("public_access", False)
            encryption = bucket.get("encryption", "disabled")
            if public:
                findings.append({
                    "category": "storage",
                    "severity": "high",
                    "title": "Publicly accessible storage",
                    "details": f"Bucket {bucket.get('name', 'unknown')} is publicly readable or writable.",
                    "evidence": bucket,
                })
            if encryption.lower() in {"disabled", "none"}:
                findings.append({
                    "category": "storage",
                    "severity": "medium",
                    "title": "Storage not encrypted at rest",
                    "details": f"Bucket {bucket.get('name', 'unknown')} lacks encryption.",
                    "evidence": bucket,
                })
        return findings

    def _check_network(self, network: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        security_groups = network.get("security_groups", [])
        for sg in security_groups:
            rules = sg.get("ingress", [])
            for rule in rules:
                if rule.get("cidr", "0.0.0.0/0") == "0.0.0.0/0" and rule.get("port", "") in {"22", "3389", "80", "443", "0"}:
                    findings.append({
                        "category": "network",
                        "severity": "high",
                        "title": "Open inbound access",
                        "details": f"Security group {sg.get('name', 'unknown')} exposes port {rule.get('port')} to the internet.",
                        "evidence": rule,
                    })
        return findings

    def _check_logging(self, logging: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        if logging.get("cloudtrail_enabled") is False:
            findings.append({
                "category": "logging",
                "severity": "medium",
                "title": "CloudTrail logging disabled",
                "details": "No centralized audit logging is configured.",
                "evidence": logging,
            })
        if logging.get("guardduty_enabled") is False:
            findings.append({
                "category": "logging",
                "severity": "medium",
                "title": "Threat detection not enabled",
                "details": "No managed detection service is enabled.",
                "evidence": logging,
            })
        return findings

    def _check_secrets(self, secrets: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for secret in secrets.get("values", []):
            if secret.get("hardcoded") or secret.get("plaintext"):
                findings.append({
                    "category": "secrets",
                    "severity": "high",
                    "title": "Hardcoded secret or plaintext credential",
                    "details": f"Secret {secret.get('name', 'unknown')} appears to be stored in plaintext or embedded in configuration.",
                    "evidence": secret,
                })
        return findings

    def _check_compute(self, compute: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for instance in compute.get("instances", []):
            if instance.get("public_ip") and instance.get("ssh_open"):
                findings.append({
                    "category": "compute",
                    "severity": "high",
                    "title": "Public instance with SSH exposed",
                    "details": f"Instance {instance.get('name', 'unknown')} is internet-facing and exposes SSH.",
                    "evidence": instance,
                })
            if instance.get("imdsv2_disabled") is False:
                findings.append({
                    "category": "compute",
                    "severity": "medium",
                    "title": "IMDSv2 not enforced",
                    "details": f"Instance {instance.get('name', 'unknown')} may be vulnerable to metadata service abuse.",
                    "evidence": instance,
                })
        return findings

    def _calculate_severity(self, findings: List[Dict[str, Any]]) -> str:
        weights = {"low": 1, "medium": 2, "high": 3}
        score = 0
        for f in findings:
            score += weights.get(f.get("severity", "low"), 1)
        if score >= 12:
            return "critical"
        if score >= 7:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def _calculate_confidence(self, findings: List[Dict[str, Any]]) -> str:
        if len(findings) >= 5:
            return "high"
        if len(findings) >= 2:
            return "medium"
        return "low"

    def _risk_score(self, findings: List[Dict[str, Any]]) -> int:
        weights = {"low": 10, "medium": 25, "high": 50}
        total = 0
        for f in findings:
            total += weights.get(f.get("severity", "low"), 10)
        return min(total, 100)

    def _classify(self, risk_score: int) -> str:
        if risk_score >= 80:
            return "critical_risk"
        if risk_score >= 50:
            return "high_risk"
        if risk_score >= 25:
            return "medium_risk"
        return "low_risk"

    def _recommended_actions(self, findings: List[Dict[str, Any]]) -> List[str]:
        actions: List[str] = []
        categories = {f["category"] for f in findings}
        if "iam" in categories:
            actions.append("Review and reduce IAM permissions to least privilege")
        if "storage" in categories:
            actions.append("Restrict public access and enable encryption for cloud storage")
        if "network" in categories:
            actions.append("Tighten security group and firewall rules to restrict inbound access")
        if "logging" in categories:
            actions.append("Enable centralized audit logs and threat detection services")
        if "secrets" in categories:
            actions.append("Move credentials to managed secret stores and remove plaintext values")
        if "compute" in categories:
            actions.append("Harden compute instances and enforce IMDSv2 + minimal public exposure")
        if not actions:
            actions.append("Continue monitoring and validate cloud controls with periodic audits")
        return actions

    def print_report(self, pretty: bool = True) -> None:
        payload = json.dumps(self.last_report, indent=2 if pretty else None, sort_keys=True)
        print(payload)


class SOCAgentOrchestrator:
    """Example orchestrator showing how a cloud-security agent fits inside a SOC."""

    def __init__(self, cloud: str = "aws", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.cloud = cloud
        self.case_id = case_id
        self.analyst = analyst
        self.cloud_agent = CloudSecurityAgent(cloud=cloud, case_id=case_id, analyst=analyst)

    def assess_cloud_posture(self, config: Dict[str, Any]) -> Dict[str, Any]:
        result = self.cloud_agent.analyze_config(config)
        return {
            "agent": "soc_orchestrator",
            "case_id": self.case_id,
            "cloud_security_result": result,
            "next_step": "escalate_to_ir" if result["summary"]["classification"] in {"high_risk", "critical_risk"} else "monitor_and_review",
            "orchestration_plan": {
                "primary_agent": "cloud_security",
                "secondary_agents": ["identity_security", "network_security", "threat_detection"],
                "decision": "review" if result["summary"]["classification"] == "low_risk" else "escalate",
            },
        }


class SOCCloudSecurityWorkflow:
    """A simple workflow model to show how a cloud-security agent works inside a multi-agent SOC stack."""

    def __init__(self, cloud: str = "aws", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.orchestrator = SOCAgentOrchestrator(cloud=cloud, case_id=case_id, analyst=analyst)

    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "workflow": "soc_cloud_security_pipeline",
            "orchestrator": self.orchestrator.assess_cloud_posture(config),
            "status": "agentic_triage_complete",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="SOC cloud security analysis agent")
    parser.add_argument("--cloud", default="aws", help="Cloud provider: aws, azure, gcp")
    parser.add_argument("--case-id", default="CASE-UNKNOWN", help="SOC case identifier")
    parser.add_argument("--analyst", default="SOC Analyst", help="Analyst or team name")
    parser.add_argument("--json", help="Path to a JSON config file to analyze")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON output")
    args = parser.parse_args()

    if not args.json:
        print("[ERROR] Please provide a JSON config file using --json", file=sys.stderr)
        return 1

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as exc:
        print(f"[ERROR] Could not read config: {exc}", file=sys.stderr)
        return 2

    try:
        workflow = SOCCloudSecurityWorkflow(cloud=args.cloud, case_id=args.case_id, analyst=args.analyst)
        result = workflow.run(config)
        if args.compact:
            print(json.dumps(result, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Analysis failed: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
