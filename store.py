import json
from datetime import datetime
from config import INBOX_FILE, TRACE_FILE, DECISIONS_FILE

def load_inbox():
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def log_trace(event_type: str, cap: str, data: dict):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "cap": cap,
        **data
    }
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def save_decisions(decisions: dict):
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)