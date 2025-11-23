"""Add Modal credentials to .env file."""

import sys
import io
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Your Modal credentials
MODAL_API_KEY = "wk-bLY0HgGSR5CiK1ix4UZ3mT"
MODAL_SECRET = "ws-U7PmwVer3BzRBdPak3nzJV"

env_file = Path(".env")

# Read existing .env if it exists
env_content = ""
if env_file.exists():
    env_content = env_file.read_text()

# Add or update Modal credentials
lines = env_content.split("\n") if env_content else []
updated_key = False
updated_secret = False

for i, line in enumerate(lines):
    if line.startswith("MODAL_API_KEY=") or line.startswith("MODAL_KEY="):
        lines[i] = f"MODAL_API_KEY={MODAL_API_KEY}"
        updated_key = True
    elif line.startswith("MODAL_SECRET="):
        lines[i] = f"MODAL_SECRET={MODAL_SECRET}"
        updated_secret = True

if not updated_key:
    lines.append(f"MODAL_API_KEY={MODAL_API_KEY}")
if not updated_secret:
    lines.append(f"MODAL_SECRET={MODAL_SECRET}")

# Write back
env_file.write_text("\n".join(lines))
print("[OK] Modal credentials added to .env file")
print(f"   MODAL_API_KEY={MODAL_API_KEY[:10]}...")
print(f"   MODAL_SECRET={MODAL_SECRET[:10]}...")

