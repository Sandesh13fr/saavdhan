"""Create the local demo officer account for the pattern map. Local only; never in production.

Password comes from SAAVDHAN_DEMO_OFFICER_PASSWORD in .env. If absent, a random one is
generated and appended to .env (gitignored). The password is never printed.
Run: .venv\\Scripts\\python scripts\\seed_demo_officer.py
"""
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv  # noqa: E402

ENV = ROOT / ".env"
load_dotenv(ENV)
from backend import auth  # noqa: E402

EMAIL = "officer@saavdhan.example"

if auth.production():
    raise SystemExit("Refusing to seed a demo account in production")
password = os.getenv("SAAVDHAN_DEMO_OFFICER_PASSWORD")
if not password:
    password = secrets.token_urlsafe(18)
    with ENV.open("a", encoding="utf-8") as f:
        f.write(f"\n# Local demo officer for the pattern map ({EMAIL}); synthetic data only\nSAAVDHAN_DEMO_OFFICER_PASSWORD={password}\n")
with auth.database() as conn:
    exists = conn.execute("SELECT 1 FROM users WHERE email=?", (EMAIL,)).fetchone()
if exists:
    auth.reset_password(EMAIL, password)
else:
    auth.provision(EMAIL, "Demo officer (synthetic)", "demo-authority", "viewer", password)
print(f"Demo officer ready: {EMAIL} (password in .env as SAAVDHAN_DEMO_OFFICER_PASSWORD)")
