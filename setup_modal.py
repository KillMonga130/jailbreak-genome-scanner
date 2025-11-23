"""Setup Modal.com for the project."""

import os
import subprocess
import sys
from pathlib import Path

def setup_modal():
    """Set up Modal.com integration."""
    print("=" * 80)
    print("MODAL.COM SETUP")
    print("=" * 80)
    print()
    
    # Check if modal is installed
    try:
        import modal
        print("✅ Modal SDK already installed")
    except ImportError:
        print("Installing Modal SDK...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "modal"])
        print("✅ Modal SDK installed")
    
    # Set up credentials
    print("\nSetting up Modal credentials...")
    
    api_key = input("Enter Modal API Key (wk-...): ").strip()
    api_secret = input("Enter Modal API Secret (ws-...): ").strip()
    
    if api_key and api_secret:
        # Set environment variables
        env_file = Path(".env")
        env_content = ""
        
        if env_file.exists():
            env_content = env_file.read_text()
        
        # Update or add Modal credentials
        lines = env_content.split("\n")
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith("MODAL_API_KEY=") or line.startswith("MODAL_KEY="):
                lines[i] = f"MODAL_API_KEY={api_key}"
                updated = True
            elif line.startswith("MODAL_SECRET="):
                lines[i] = f"MODAL_SECRET={api_secret}"
                updated = True
        
        if not updated:
            lines.append(f"MODAL_API_KEY={api_key}")
            lines.append(f"MODAL_SECRET={api_secret}")
        
        env_file.write_text("\n".join(lines))
        print("✅ Credentials saved to .env file")
    else:
        print("⚠️  Credentials not provided")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Deploy models to Modal:")
    print("   modal deploy modal_deploy.py")
    print()
    print("2. Get the endpoint URL from Modal dashboard")
    print()
    print("3. Set endpoint in .env:")
    print("   MODAL_ENDPOINT_JAILBREAK_GENOME_SCANNER=https://your-username--jailbreak-genome-scanner-serve.modal.run")
    print()
    print("4. Update dashboard to use Modal instead of Lambda Cloud")
    print()

if __name__ == "__main__":
    setup_modal()

