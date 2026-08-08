def run_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all available specialist agents and write to memory."""
        results: Dict[str, Any] = {
            "orchestrator": {"case_id": self.case_id, "status": "completed"},
            "specialists": {},
            "aggregated_data": {"mitre": [], "tools": [], "actions": []}
        }

        # Run Agents (assuming you have the methods defined)
        if incident.get("observables"):
            results["specialists"]["threat_intel"] = self._run_threat_intel(incident["observables"])
        if incident.get("logs"):
            results["specialists"]["log_analysis"] = self._run_log_analysis(incident["logs"])

        # EXTRACT REAL DYNAMIC DATA FROM LLMS
        mitre_set, tool_set, actions_list = set(), set(), []
        
        for agent_name, data in results["specialists"].items():
            # Deep search the JSON for our required keys
            data_str = json.dumps(data)
            if "mitre_tactics" in data_str:
                # Basic extraction for hackathon speed
                for key in ["threat_intel_result", "log_analysis_result"]:
                    if data and key in data:
                        summary = data[key].get("summary", {})
                        mitre_set.update(summary.get("mitre_tactics", []))
                        tool_set.update(summary.get("tools_utilized", []))
                        if summary.get("autonomous_action"):
                            actions_list.append(summary["autonomous_action"])

        results["aggregated_data"]["mitre"] = list(mitre_set)
        results["aggregated_data"]["tools"] = list(tool_set)
        results["aggregated_data"]["actions"] = actions_list
        
        results["decision"] = self._decide_priority(results["specialists"])
        results["recommended_next_step"] = self._next_step(results["decision"])

        # REAL SHARED MEMORY (Writes to disk)
        try:
            memory_file = self.root_dir / "incident_memory.json"
            memory_data = []
            if memory_file.exists():
                with open(memory_file, "r") as f:
                    memory_data = json.load(f)
            memory_data.append({"case": self.case_id, "decision": results["decision"], "mitre": list(mitre_set)})
            with open(memory_file, "w") as f:
                json.dump(memory_data, f)
        except Exception:
            pass # Ignore memory write errors during demo

        return results
