import json
from config import OUTBOX_DIR
from store import log_trace

REVERSIBLE_ACTIONS = ["draft", "label", "archive", "defer"]
IRREVERSIBLE_ACTIONS = ["send", "delete"]

def execute_action(action: str, payload: dict, dry_run: bool = False, auto_approve: bool = False) -> bool:
    """
    Gates irreversible actions behind approval or --dry-run.
    """
    msg_id = payload.get("id", "unknown")
    if action in IRREVERSIBLE_ACTIONS:
        log_trace("gate", "R3", {
            "msg_id": msg_id,
            "action": action,
            "dry_run": dry_run,
            "payload_summary": f"Sending to {payload.get('to')}: {payload.get('subject')}"
        })
        
        if dry_run:
            print(f"[DRY-RUN GATE] Irreversible action '{action}' blocked for message {msg_id}.")
            print(f"               Would write to outbox/: {payload.get('subject')} -> {payload.get('to')}")
            return False
            
        if not auto_approve:
            ans = input(f"[HUMAN GATE] Approve irreversible action '{action}' for message {msg_id}? (y/n): ").strip().lower()
            if ans != 'y':
                print(f"[GATE DENIED] Action '{action}' canceled by user.")
                return False

        # Execute Send: Write to outbox/
        outbox_file = OUTBOX_DIR / f"{msg_id}.json"
        with open(outbox_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"[OUTBOX WRITTEN] Sent message {msg_id} written to {outbox_file}")
        return True
    else:
        # Reversible action
        return True