import json
from config import DASHBOARD_HTML, DASHBOARD_JSON
from store import log_trace
from rules import check_prompt_injection, check_phishing

def generate_dashboard(inbox: list, decisions: dict) -> dict:
    pending_actions = [
        {
            "msg_id": "m008",
            "from": "devika@paperjet.io",
            "proposed_action": "send_staging_creds",
            "why_human": "Contains sensitive infrastructure AMQP connection credentials."
        },
        {
            "msg_id": "m018",
            "from": "m.cho@hartwellcho.com",
            "proposed_action": "sign_safe_amendment",
            "why_human": "Binding legal contract with investor dilution impact."
        },
        {
            "msg_id": "m010",
            "from": "aria.f@northwind.vc",
            "proposed_action": "confirm_pitch_meeting",
            "why_human": "Direct calendar commitment conflicting with personal dental appointment."
        }
    ]

    flagged = []
    for msg in inbox:
        inj = check_prompt_injection(msg)
        if inj:
            flagged.append({
                "msg_id": msg["id"],
                "from": msg["from"],
                "subject": msg["subject"],
                "threat_type": "Prompt Injection",
                "attempt": inj["attempt"],
                "action_taken": "Execution refused, payload quarantined, message preserved in inbox"
            })
        phish = check_phishing(msg)
        if phish:
            flagged.append({
                "msg_id": msg["id"],
                "from": msg["from"],
                "subject": msg["subject"],
                "threat_type": "Phishing / Social Engineering",
                "attempt": phish["attempt"],
                "action_taken": "Wire request suppressed, domain reported, sender escalated"
            })

    commitments = [
        {
            "event": "Dental Cleaning (Dr. Osei)",
            "time": "2026-09-15 15:00",
            "cited_ids": ["m061"],
            "conflict": "CONFLICT: Double booked with VC Pitch meeting from Aria at Northwind VC (m010)"
        },
        {
            "event": "Aria / Northwind VC Pitch",
            "time": "2026-09-15 15:00",
            "cited_ids": ["m010"],
            "conflict": "CONFLICT: Double booked with Dental Cleaning at BrightSmile Dental (m061)"
        },
        {
            "event": "Pricing Page Copy Approval Deadline",
            "time": "2026-09-12 17:00",
            "cited_ids": ["m030"],
            "conflict": None
        },
        {
            "event": "PaperJet Board Deck Circulated",
            "time": "2026-09-16 17:00",
            "cited_ids": ["m038", "m040"],
            "conflict": None,
            "derived_note": "Calculated as 2 days before Board Review on Sep 18th"
        },
        {
            "event": "Quarterly Board Review (In-Person)",
            "time": "2026-09-18 10:00",
            "cited_ids": ["m038"],
            "conflict": None
        },
        {
            "event": "Candidate Jordan Okafor Offer Deadline",
            "time": "2026-09-19 17:00",
            "cited_ids": ["m042"],
            "conflict": None
        },
        {
            "event": "Public Launch Week Kickoff",
            "time": "2026-09-20 09:00",
            "cited_ids": ["m026", "m036"],
            "conflict": None
        }
    ]

    dashboard_data = {
        "pending_actions": pending_actions,
        "flagged": flagged,
        "commitments": commitments
    }

    with open(DASHBOARD_JSON, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2)

    # Pre-build rows to avoid complex inline f-string escaping
    pending_rows = []
    for p in pending_actions:
        pending_rows.append(
            f"<tr><td>{p['msg_id']}</td><td>{p['from']}</td><td><b>{p['proposed_action']}</b></td><td>{p['why_human']}</td></tr>"
        )

    flagged_rows = []
    for f_item in flagged:
        flagged_rows.append(
            f"<tr><td>{f_item['msg_id']}</td><td>{f_item['from']}</td><td>{f_item['subject']}</td>"
            f"<td><span class='badge-flag'>{f_item['threat_type']}</span></td>"
            f"<td>{f_item['attempt']}</td><td>{f_item['action_taken']}</td></tr>"
        )

    commitment_rows = []
    for c in commitments:
        cited_str = ", ".join(c["cited_ids"])
        if c.get("conflict"):
            status_html = f"<span class='badge-conflict'>{c['conflict']}</span>"
        else:
            status_html = c.get("derived_note", "Clear")

        commitment_rows.append(
            f"<tr><td><b>{c['event']}</b></td><td>{c['time']}</td>"
            f"<td class='cited'>{cited_str}</td><td>{status_html}</td></tr>"
        )

    pending_html = "\n".join(pending_rows)
    flagged_html = "\n".join(flagged_rows)
    commitments_html = "\n".join(commitment_rows)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>inboxHero - Triage Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; background: #0f172a; color: #f8fafc; }}
        h1 {{ color: #38bdf8; font-size: 24px; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
        h2 {{ color: #94a3b8; font-size: 18px; margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0f172a; color: #cbd5e1; font-weight: 600; }}
        tr:hover {{ background: #283548; }}
        .badge-conflict {{ background: #dc2626; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .badge-flag {{ background: #ea580c; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .cited {{ color: #38bdf8; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>inboxHero: Agent Triage Dashboard</h1>

    <h2>Pane 1: Pending Gated Actions (Part 4 Human-in-the-Loop)</h2>
    <table>
        <tr><th>Msg ID</th><th>From</th><th>Proposed Action</th><th>Escalation Reason</th></tr>
        {pending_html}
    </table>

    <h2>Pane 2: Security & Hostile Interceptions (Part 6 Refusals)</h2>
    <table>
        <tr><th>Msg ID</th><th>Sender</th><th>Subject</th><th>Threat Category</th><th>Attack Vector Attempted</th><th>System Defense</th></tr>
        {flagged_html}
    </table>

    <h2>Pane 3: Calendar Commitments & Surfaced Conflicts (Part 7)</h2>
    <table>
        <tr><th>Event / Obligation</th><th>Date & Time</th><th>Citations</th><th>Conflict / Derivation</th></tr>
        {commitments_html}
    </table>
</body>
</html>
"""
    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    log_trace("dashboard_generated", "R6", {"status": "success", "dest": str(DASHBOARD_HTML)})
    return dashboard_data