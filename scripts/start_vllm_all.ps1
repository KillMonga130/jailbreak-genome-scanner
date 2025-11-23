# PowerShell script to start vLLM on all Lambda instances
# This is a quick wrapper for the Python setup script

Write-Host "=== Starting vLLM on All Lambda Instances ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Run the setup script
Write-Host "Running setup script..." -ForegroundColor Yellow
Write-Host ""

python scripts/setup_all_instances.py

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Start SSH tunnels: .\scripts\setup_ssh_tunnels.ps1" -ForegroundColor Gray
Write-Host "2. Test connections:" -ForegroundColor Gray
Write-Host "   curl http://localhost:8000/v1/models  # Mistral" -ForegroundColor Gray
Write-Host "   curl http://localhost:8001/v1/models  # Qwen" -ForegroundColor Gray
Write-Host "   curl http://localhost:8002/v1/models  # H100" -ForegroundColor Gray
Write-Host "3. Run evaluations in the dashboard!" -ForegroundColor Gray
Write-Host ""

