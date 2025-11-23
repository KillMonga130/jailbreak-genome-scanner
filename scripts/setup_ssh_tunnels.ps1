# PowerShell script to set up SSH tunnels for Lambda Cloud instances
# This script creates SSH tunnels for all your Lambda instances

Write-Host "=== Lambda Cloud SSH Tunnel Setup ===" -ForegroundColor Cyan
Write-Host ""

# Instance configurations (matching your Lambda Cloud dashboard)
$instances = @(
    @{
        Name = "H100_FOR_THE_HACKATHON"
        IP = "209.20.159.141"
        LocalPort = 8002
        RemotePort = 8000
        User = "ubuntu"
    },
    @{
        Name = "Mistral_7B_Instruct"
        IP = "129.80.191.122"
        LocalPort = 8000
        RemotePort = 8000
        User = "ubuntu"
    },
    @{
        Name = "Qwen_7B_Chat"
        IP = "150.136.220.151"
        LocalPort = 8001
        RemotePort = 8000
        User = "ubuntu"
    }
)

Write-Host "Available instances:" -ForegroundColor Yellow
foreach ($instance in $instances) {
    Write-Host "  - $($instance.Name): $($instance.IP) -> localhost:$($instance.LocalPort)" -ForegroundColor White
}
Write-Host ""

# Check if SSH is available
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshPath) {
    Write-Host "ERROR: SSH not found. Please install OpenSSH or use WSL." -ForegroundColor Red
    exit 1
}

Write-Host "Setting up SSH tunnels..." -ForegroundColor Cyan
Write-Host ""

$tunnelProcesses = @()

foreach ($instance in $instances) {
    $localPort = $instance.LocalPort
    $remoteHost = $instance.IP
    $remotePort = $instance.RemotePort
    
    Write-Host "Setting up tunnel for $($instance.Name)..." -ForegroundColor Yellow
    Write-Host "  Local port: $localPort" -ForegroundColor Gray
    Write-Host "  Remote: ${remoteHost}:${remotePort}" -ForegroundColor Gray
    
    # Check if port is already in use
    $portInUse = Get-NetTCPConnection -LocalPort $localPort -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "  WARNING: Port $localPort is already in use!" -ForegroundColor Yellow
        Write-Host "  You may need to close the existing connection or use a different port." -ForegroundColor Yellow
        continue
    }
    
    # Start SSH tunnel in background
    $sshKeyPath = "moses.pem"
    if (-not (Test-Path $sshKeyPath)) {
        Write-Host "  WARNING: SSH key not found at $sshKeyPath" -ForegroundColor Yellow
        Write-Host "  Attempting without key (will use default SSH key)" -ForegroundColor Yellow
        $sshArgs = @("-N", "-L", "${localPort}:localhost:${remotePort}", "$($instance.User)@${remoteHost}")
    } else {
        $sshArgs = @("-i", $sshKeyPath, "-N", "-L", "${localPort}:localhost:${remotePort}", "$($instance.User)@${remoteHost}")
    }
    
    try {
        $process = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -PassThru -WindowStyle Hidden
        $tunnelProcesses += @{
            Name = $instance.Name
            Process = $process
            Port = $localPort
        }
        Write-Host "  ✓ Tunnel started (PID: $($process.Id))" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to start tunnel: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "=== Tunnel Status ===" -ForegroundColor Cyan
Write-Host ""

if ($tunnelProcesses.Count -eq 0) {
    Write-Host "No tunnels were started." -ForegroundColor Yellow
    exit 1
}

foreach ($tunnel in $tunnelProcesses) {
    $process = $tunnel.Process
    Start-Sleep -Milliseconds 500  # Give process time to start
    if ($process.HasExited) {
        Write-Host "  $($tunnel.Name): ✗ Stopped (exit code: $($process.ExitCode))" -ForegroundColor Red
    }
    else {
        Write-Host "  $($tunnel.Name): ✓ Running (PID: $($process.Id), Port: $($tunnel.Port))" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Testing Connections ===" -ForegroundColor Cyan
Write-Host ""

foreach ($tunnel in $tunnelProcesses) {
    if (-not $tunnel.Process.HasExited) {
        $testUrl = "http://localhost:$($tunnel.Port)/v1/models"
        Write-Host "Testing $($tunnel.Name) at $testUrl..." -ForegroundColor Yellow
        
        try {
            $response = Invoke-WebRequest -Uri $testUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
            Write-Host "  ✓ Connection successful! vLLM is running." -ForegroundColor Green
        }
        catch {
            Write-Host "  ⚠ Tunnel active but vLLM may not be running on instance" -ForegroundColor Yellow
            Write-Host "    This is OK - the tunnel is working, but vLLM needs to be started." -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "=== Usage ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoints (use these in dashboard):" -ForegroundColor White
foreach ($tunnel in $tunnelProcesses) {
    if (-not $tunnel.Process.HasExited) {
        Write-Host "  $($tunnel.Name): http://localhost:$($tunnel.Port)/v1/chat/completions" -ForegroundColor Gray
    }
}
Write-Host ""
Write-Host "Tunnels are running in the background. To stop them:" -ForegroundColor White
Write-Host "  .\scripts\stop_ssh_tunnels.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Or manually:" -ForegroundColor White
Write-Host "  Stop-Process -Id [PID]" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANT: Keep this PowerShell window open to maintain tunnels!" -ForegroundColor Yellow
Write-Host ""
