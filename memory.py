import json
from config import PREFS_FILE
from store import log_trace

def load_preferences() -> dict:
    if not PREFS_FILE.exists():
        return {
            "legal_cc": [],
            "no_meetings_before": "11:00",
            "extracted_from": []
        }
    with open(PREFS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_preferences(prefs: dict):
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)

def extract_and_store_preferences(messages: list):
    prefs = load_preferences()
    updated = False
    
    for msg in messages:
        # Check m015: Loop Priya into Hartwell & Cho
        if msg["id"] == "m015" and "m015" not in prefs["extracted_from"]:
            if "priya@paperjet.io" not in prefs["legal_cc"]:
                prefs["legal_cc"].append("priya@paperjet.io")
            prefs["extracted_from"].append("m015")
            updated = True
            log_trace("preference_recorded", "R4", {
                "source_msg": "m015",
                "preference": "CC priya@paperjet.io on Hartwell & Cho legal mail"
            })
            
        # Check m041: No meetings before 11:00am
        if msg["id"] == "m041" and "m041" not in prefs["extracted_from"]:
            prefs["no_meetings_before"] = "11:00"
            prefs["extracted_from"].append("m041")
            updated = True
            log_trace("preference_recorded", "R4", {
                "source_msg": "m041",
                "preference": "Do not accept meetings before 11:00am; offer 11:00am or later"
            })

    if updated:
        save_preferences(prefs)
    return prefs