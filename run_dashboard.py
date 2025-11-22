"""Run the gamified Arena Dashboard."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    dashboard_path = Path(__file__).parent / "dashboard" / "arena_dashboard.py"
    
    print("Starting Jailbreak Arena Dashboard...")
    print("Opening in browser...")
    print("\nNote: Make sure Streamlit is installed:")
    print("   pip install streamlit plotly")
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", "8501",
        "--server.headless", "true"
    ])

