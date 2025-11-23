# PowerShell script to set up SSH tunnel for Qwen instance
# This instance has port 8000 blocked, so we use SSH tunnel on port 8001

Write-Host "Setting up SSH tunnel for Qwen instance..." -ForegroundColor Cyan
Write-Host "Instance IP: 150.136.220.151" -ForegroundColor Yellow
Write-Host "Local port: 8001" -ForegroundColor Yellow
Write-Host "Remote port: 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "This will forward localhost:8001 to the instance's port 8000" -ForegroundColor Green
Write-Host "Use endpoint: http://localhost:8001/v1/chat/completions" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host ""

$sshKey = "moses.pem"
$instanceIP = "150.136.220.151"
$localPort = "8001"  # Note: You can change this if 8001 is already in use
$remotePort = "8000"

# Check if SSH key exists
if (-not (Test-Path $sshKey)) {
    Write-Host "ERROR: SSH key not found: $sshKey" -ForegroundColor Red
    Write-Host "Please make sure moses.pem is in the current directory" -ForegroundColor Yellow
    exit 1
}

# Start SSH tunnel
Write-Host "Starting SSH tunnel..." -ForegroundColor Cyan
ssh -i $sshKey -N -L ${localPort}:localhost:${remotePort} ubuntu@${instanceIP}

