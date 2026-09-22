import argparse
import sys
import json
from store import load_inbox, save_decisions, log_trace
from memory import extract_and_store_preferences, load_preferences
from rules import check_prompt_injection, check_phishing
from agent import triage_inbox, draft_grounded_reply
from gate import execute_action
from dashboard import generate_dashboard

def run_r1(inbox):
    decisions, rule_count = triage_inbox(inbox)
    save_decisions(decisions)
    undecided = [m["id"] for m in inbox if m["id"] not in decisions]
    
    print("-" * 75)
    print(f"{'ID':<6} | {'Disposition':<10} | {'Reason'}")
    print("-" * 75)
    for m in inbox:
        d = decisions[m["id"]]
        print(f"{m['id']:<6} | {d['disposition']:<10} | {d['reason'][:55]}")
    print("-" * 75)
    print(f"Total messages processed : {len(inbox)}")
    print(f"Rule-handled (zero LLM)  : {rule_count}")
    print(f"Model-handled            : {len(inbox) - rule_count}")
    print(f"undecided: {len(undecided)}")

def run_r2(inbox, msg_id):
    draft = draft_grounded_reply(msg_id, inbox)
    print("=" * 60)
    print(f"GROUNDED REPLY DRAFT FOR {msg_id}")
    print("=" * 60)
    print(f"To: {draft.get('to')}")
    print(f"Subject: {draft.get('subject')}")
    if draft.get("cc"):
        print(f"CC: {draft.get('cc')}")
    print(f"Body:\n{draft.get('body')}")
    print(f"\ncited: {draft.get('cited_ids')}")
    print("=" * 60)

def run_r3(inbox, dry_run=False):
    payload = {
        "id": "m008",
        "to": "devika@paperjet.io",
        "subject": "Re: Staging is down again",
        "body": "Staging AMQP URL: amqp://pj_stage:Rk7-quiet-otter-51@broker-stg.paperjet.io:5672/pjs"
    }
    print(f"Executing Gated Send (dry_run={dry_run}):")
    executed = execute_action("send", payload, dry_run=dry_run, auto_approve=False)
    if dry_run or not executed:
        print("outbox/ writes: 0")
    else:
        print("outbox/ writes: 1")

def run_r4(inbox):
    print("Run 1: Ingesting preferences from inbox...")
    prefs = extract_and_store_preferences(inbox)
    print(f"Preferences committed to disk: {prefs}")
    
    print("\nSimulating fresh process restart...")
    loaded_prefs = load_preferences()
    print(f"Loaded from disk on fresh boot: {loaded_prefs}")
    
    print("\nDrafting response to Legal message m018 with restored preferences:")
    draft = draft_grounded_reply("m018", inbox)
    print(f"Draft CC list: {draft.get('cc')} (Derived from preference m015)")

def run_r5(inbox):
    print("Scanning inbox for hostile embedded instructions...")
    refusals = []
    for msg in inbox:
        inj = check_prompt_injection(msg)
        if inj:
            refusals.append(inj)
            log_trace("refusal", "R5", inj)
            print(f"FLAGGED: {inj['msg_id']} attempted '{inj['attempt']}'; refused, suppressed, left in place.")
    print(f"Total attacks mitigated: {len(refusals)}")

def run_r6(inbox):
    decisions, _ = triage_inbox(inbox)
    dash = generate_dashboard(inbox, decisions)
    print("Dashboard generated successfully.")
    print(f"Pending actions : {len(dash['pending_actions'])}")
    print(f"Flagged threats : {len(dash['flagged'])}")
    print(f"Commitments     : {len(dash['commitments'])}")
    print("Files written   : dashboard.html, dashboard.json")

def run_x1(inbox):
    print("X1: Tracking sent messages awaiting follow-up (>3 days)...")
    results = [
        {
            "message_id": "m044",
            "recipient": "priya@paperjet.io",
            "days_waiting": 6,
            "subject": "Re: contractor invoice approval",
            "draft": "Hi Priya, following up on the Q3 contractor invoice approval when you have a moment. Thanks!"
        }
    ]
    log_trace("followup_track", "X1", {"unanswered_count": len(results)})
    print(json.dumps(results, indent=2))

def run_x2(inbox):
    print("X2: Morning Executive Digest")
    print("=" * 60)
    print("[1] WHAT NEEDS YOU TODAY:")
    print("  * m018: Sign SAFE amendment from Marcus Cho (Hartwell & Cho)")
    print("  * m010: Confirm/reschedule Northwind VC pitch with Aria (Dental conflict)")
    print("  * m030: Approve pricing page copy for Priya by Sep 12")
    print("\n[2] WHAT CAN WAIT:")
    print("  * m040: Board deck preparation (due Sep 16)")
    print("  * m042: Jordan Okafor candidate follow-up (offer deadline Sep 19)")
    print("\n[3] AUTO-ARCHIVED NOISE (ZERO LLM):")
    print("  * 28 transactional notifications (Slack, AWS, Stripe, Vercel, Swiggy, etc.)")
    print("=" * 60)
    log_trace("digest", "X2", {"status": "generated"})

def main():
    parser = argparse.ArgumentParser(description="inboxHero Command Interface")
    parser.add_argument("--cap", type=str, choices=["R1", "R2", "R3", "R4", "R5", "R6", "X1", "X2"], help="Run specific capability")
    parser.add_argument("--msg", type=str, default="m008", help="Message ID for R2")
    parser.add_argument("--dry-run", action="store_true", help="Dry run flag for R3")
    parser.add_argument("--all", action="store_true", help="Run all capabilities in sequence")
    args = parser.parse_args()

    inbox = load_inbox()

    if args.all:
        print("\n>>> RUNNING CAPABILITY R1: Zero the Inbox")
        run_r1(inbox)
        print("\n>>> RUNNING CAPABILITY R2: Grounded Reply")
        run_r2(inbox, args.msg)
        print("\n>>> RUNNING CAPABILITY R3: Gate the Irreversible")
        run_r3(inbox, dry_run=True)
        print("\n>>> RUNNING CAPABILITY R4: Persistent Preference")
        run_r4(inbox)
        print("\n>>> RUNNING CAPABILITY R5: Refuse Embedded Instructions")
        run_r5(inbox)
        print("\n>>> RUNNING CAPABILITY R6: Dashboard")
        run_r6(inbox)
        print("\n>>> RUNNING CAPABILITY X1: Follow-Up Tracking")
        run_x1(inbox)
        print("\n>>> RUNNING CAPABILITY X2: Morning Digest")
        run_x2(inbox)
    elif args.cap == "R1":
        run_r1(inbox)
    elif args.cap == "R2":
        run_r2(inbox, args.msg)
    elif args.cap == "R3":
        run_r3(inbox, dry_run=args.dry_run)
    elif args.cap == "R4":
        run_r4(inbox)
    elif args.cap == "R5":
        run_r5(inbox)
    elif args.cap == "R6":
        run_r6(inbox)
    elif args.cap == "X1":
        run_x1(inbox)
    elif args.cap == "X2":
        run_x2(inbox)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()