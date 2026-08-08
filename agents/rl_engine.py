import json
from pathlib import Path

class RLMemoryEngine:
    def __init__(self, db_path="rl_q_table.json"):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self):
        if not self.db_path.exists():
            with open(self.db_path, "w") as f:
                json.dump({"T1078 - Valid Accounts": {"Revoke IAM": 5, "Ignore": -2}}, f)

    def get_best_action(self, threat_type: str) -> str:
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
            for known_threat, actions in data.items():
                if known_threat.lower() in threat_type.lower() or threat_type.lower() in known_threat.lower():
                    if actions:
                        return max(actions, key=actions.get)
            return "No historical RL data. Agent exploring new actions."
        except Exception:
            return "RL memory unreadable."

    def update_reward(self, threat_type: str, action: str, reward: int):
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
            if threat_type not in data:
                data[threat_type] = {}
            if action not in data[threat_type]:
                data[threat_type][action] = 0
            data[threat_type][action] += reward
            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"RL Update Failed: {e}")
