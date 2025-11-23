# PowerShell script to stop all SSH tunnel processes

Write-Host "=== Stopping SSH Tunnels ===" -ForegroundColor Cyan
Write-Host ""

# Find all SSH processes with port forwarding
$sshProcesses = Get-Process -Name ssh -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "* -L *" -or $_.CommandLine -like "* -N *"
}

if ($sshProcesses.Count -eq 0) {
    Write-Host "No SSH tunnel processes found." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($sshProcesses.Count) SSH tunnel process(es):" -ForegroundColor Yellow
foreach ($proc in $sshProcesses) {
    Write-Host "  PID: $($proc.Id) - $($proc.ProcessName)" -ForegroundColor White
}

Write-Host ""
$confirm = Read-Host "Stop all SSH tunnels? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

foreach ($proc in $sshProcesses) {
    try {
        Stop-Process -Id $proc.Id -Force
        Write-Host "  ✓ Stopped PID: $($proc.Id)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to stop PID: $($proc.Id) - $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "All tunnels stopped." -ForegroundColor Green

