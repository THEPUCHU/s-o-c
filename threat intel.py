"""SOC-focused threat intelligence analysis agent.

This module acts as a specialist threat-intel agent in an agentic SOC pipeline.
It enriches suspicious observables (IP addresses, domains, hashes, URLs, email
addresses) with contextual intelligence, risk scoring, and recommended action.

Usage:
    python "threat intel.py" --json indicators.json --case-id INC-1001 --analyst "SOC Analyst"
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List


class ThreatIntelAgent:
    """Specialist threat intel agent for SOC workflows."""

    def __init__(self, source: str = "internal-ti", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.source = source
        self.case_id = case_id
        self.analyst = analyst
        self.last_report: Dict[str, Any] = {}

    def enrich_observable(self, observable: Dict[str, Any]) -> Dict[str, Any]:
        value = observable.get("value", "")
        type_ = observable.get("type", "unknown").lower()
        severity = observable.get("severity", "medium")

        known_bad = self._check_known_bad(value, type_)
        reputation = self._score_reputation(value, type_, known_bad)
        tags = self._tags_for_observable(value, type_, known_bad)
        is_malicious = bool(known_bad or reputation >= 70)

        result = {
            "observable": {
                "value": value,
                "type": type_,
                "severity": severity,
            },
            "intel": {
                "known_bad": known_bad,
                "reputation_score": reputation,
                "malicious": is_malicious,
                "tags": tags,
            },
            "recommended_actions": self._recommended_actions(type_, is_malicious),
        }
        return result

    def enrich_batch(self, observables: List[Dict[str, Any]]) -> Dict[str, Any]:
        enriched = [self.enrich_observable(item) for item in observables]
        malicious_count = sum(1 for item in enriched if item["intel"]["malicious"])
        max_score = max((item["intel"]["reputation_score"] for item in enriched), default=0)

        report = {
            "agent": "threat_intelligence",
            "case_id": self.case_id,
            "analyst": self.analyst,
            "source": self.source,
            "status": "completed",
            "summary": {
                "observables_count": len(enriched),
                "malicious_count": malicious_count,
                "highest_reputation_score": max_score,
                "overall_risk": self._overall_risk(malicious_count, max_score),
            },
            "observables": enriched,
        }
        self.last_report = report
        return report

    def _check_known_bad(self, value: str, type_: str) -> bool:
        bad_domains = ["malware.example", "phishing.example", "r57shell.net", "c2.example"]
        bad_ips = ["198.51.100.10", "203.0.113.55", "10.0.0.99"]
        bad_hashes = ["abc123def456", "deadbeef", "ff11aa22"]
        bad_urls = ["http://malware.example/download", "https://phishing.example/login"]

        if type_ == "domain" and value.lower() in [d.lower() for d in bad_domains]:
            return True
        if type_ == "ip" and value in bad_ips:
            return True
        if type_ == "hash" and value.lower() in [h.lower() for h in bad_hashes]:
            return True
        if type_ == "url" and value.lower() in [u.lower() for u in bad_urls]:
            return True

        # heuristic checks for suspicious patterns
        if type_ == "domain" and ("cdn" in value.lower() or "bit.ly" in value.lower()):
            return True
        if type_ == "url" and ("download" in value.lower() or "login" in value.lower()):
            return True
        return False

    def _score_reputation(self, value: str, type_: str, known_bad: bool) -> int:
        if known_bad:
            return 95

        score = 10
        if type_ == "ip":
            score += 25
        if type_ == "domain":
            score += 15
        if type_ == "url":
            score += 20
        if type_ == "hash":
            score += 35
        if "evil" in value.lower() or "malware" in value.lower() or "phish" in value.lower():
            score += 20
        if "download" in value.lower() or "exe" in value.lower():
            score += 15
        return min(score, 100)

    def _tags_for_observable(self, value: str, type_: str, known_bad: bool) -> List[str]:
        tags: List[str] = []
        if known_bad:
            tags.append("known_bad")
        if type_ == "ip":
            tags.append("network")
        if type_ == "domain":
            tags.append("domain")
        if type_ == "url":
            tags.append("url")
        if type_ == "hash":
            tags.append("file_hash")
        if "download" in value.lower() or "exe" in value.lower():
            tags.append("payload")
        if "login" in value.lower() or "credential" in value.lower():
            tags.append("credential_target")
        if not tags:
            tags.append("unknown")
        return tags

    def _recommended_actions(self, type_: str, malicious: bool) -> List[str]:
        if not malicious:
            return ["Continue monitoring and enrich with additional telemetry"]
        actions = [
            "Block the observable at network and endpoint controls",
            "Search SIEM and EDR for historical exposure",
            "Review related alerts and impacted assets",
        ]
        if type_ in {"domain", "url"}:
            actions.append("Check DNS and web proxy logs for related communications")
        if type_ in {"ip", "domain"}:
            actions.append("Review firewall and IDS logs for connections to the indicator")
        if type_ == "hash":
            actions.append("Inspect host artifacts and file execution lineage")
        return actions

    def _overall_risk(self, malicious_count: int, highest_score: int) -> str:
        if malicious_count > 0 or highest_score >= 80:
            return "high"
        if highest_score >= 50:
            return "medium"
        return "low"

    def print_report(self, pretty: bool = True) -> None:
        payload = json.dumps(self.last_report, indent=2 if pretty else None, sort_keys=True)
        print(payload)


class SOCAgentOrchestrator:
    """Coordination layer for threat intel enrichment in a SOC pipeline."""

    def __init__(self, source: str = "internal-ti", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.source = source
        self.case_id = case_id
        self.analyst = analyst
        self.ti_agent = ThreatIntelAgent(source=source, case_id=case_id, analyst=analyst)

    def enrich_case(self, observables: List[Dict[str, Any]]) -> Dict[str, Any]:
        result = self.ti_agent.enrich_batch(observables)
        return {
            "agent": "soc_orchestrator",
            "case_id": self.case_id,
            "threat_intel_result": result,
            "next_step": "escalate_to_ir" if result["summary"]["overall_risk"] == "high" else "monitor_and_review",
            "orchestration_plan": {
                "primary_agent": "threat_intelligence",
                "secondary_agents": ["malware_analysis", "cloud_security", "compliance_analysis"],
                "decision": "escalate" if result["summary"]["overall_risk"] == "high" else "review",
            },
        }


class SOCThreatIntelWorkflow:
    """Example workflow showing threat intelligence as part of a larger SOC agent orchestration."""

    def __init__(self, source: str = "internal-ti", case_id: str = "CASE-UNKNOWN", analyst: str = "SOC Analyst"):
        self.orchestrator = SOCAgentOrchestrator(source=source, case_id=case_id, analyst=analyst)

    def run(self, observables: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "workflow": "soc_threat_intel_pipeline",
            "orchestrator": self.orchestrator.enrich_case(observables),
            "status": "agentic_threat_intel_triage_complete",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="SOC threat intelligence analysis agent")
    parser.add_argument("--json", help="Path to a JSON file containing observables")
    parser.add_argument("--case-id", default="CASE-UNKNOWN", help="SOC case identifier")
    parser.add_argument("--analyst", default="SOC Analyst", help="Analyst or team name")
    parser.add_argument("--source", default="internal-ti", help="Threat intel source label")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON output")
    args = parser.parse_args()

    if not args.json:
        print("[ERROR] Please provide a JSON file using --json", file=sys.stderr)
        return 1

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as exc:
        print(f"[ERROR] Could not read input: {exc}", file=sys.stderr)
        return 2

    observables = payload.get("observables", payload if isinstance(payload, list) else [])
    if not isinstance(observables, list):
        print("[ERROR] JSON must contain a list of observables or an object with an 'observables' list.", file=sys.stderr)
        return 3

    try:
        workflow = SOCThreatIntelWorkflow(source=args.source, case_id=args.case_id, analyst=args.analyst)
        result = workflow.run(observables)
        if args.compact:
            print(json.dumps(result, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Analysis failed: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
