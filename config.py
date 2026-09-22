import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox.json"
OUTBOX_DIR = BASE_DIR / "outbox"
TRACE_FILE = BASE_DIR / "trace.jsonl"
PREFS_FILE = BASE_DIR / "prefs.json"
DECISIONS_FILE = BASE_DIR / "decisions.json"
DASHBOARD_HTML = BASE_DIR / "dashboard.html"
DASHBOARD_JSON = BASE_DIR / "dashboard.json"

OUTBOX_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")