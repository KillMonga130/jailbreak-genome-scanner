"""Add Modal endpoint to .env file."""

import sys
import io
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Modal endpoint from deployment
MODAL_ENDPOINT_CHAT = "https://killmonga130--jailbreak-genome-scanner-chat-completions.modal.run"

env_file = Path(".env")

# Read existing .env if it exists
env_content = ""
if env_file.exists():
    env_content = env_file.read_text()

# Add or update Modal endpoint
lines = env_content.split("\n") if env_content else []
updated = False

for i, line in enumerate(lines):
    if line.startswith("MODAL_ENDPOINT_CHAT="):
        lines[i] = f"MODAL_ENDPOINT_CHAT={MODAL_ENDPOINT_CHAT}"
        updated = True
        break

if not updated:
    lines.append(f"MODAL_ENDPOINT_CHAT={MODAL_ENDPOINT_CHAT}")

# Write back
env_file.write_text("\n".join(lines))
print("[OK] Modal endpoint added to .env file")
print(f"   MODAL_ENDPOINT_CHAT={MODAL_ENDPOINT_CHAT}")

