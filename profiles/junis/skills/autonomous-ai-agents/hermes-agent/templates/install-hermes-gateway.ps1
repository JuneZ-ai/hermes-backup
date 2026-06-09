<#
.SYNOPSIS
    Install Hermes Gateway as a Windows Scheduled Task for WSL persistence
.DESCRIPTION
    Creates a Windows scheduled task (SYSTEM account) that starts WSL + Hermes Gateway
    at boot. The task holds a wsl.exe reference, keeping the WSL VM alive even when
    the last terminal window is closed — something no systemd service can do on WSL.

    Run from Windows PowerShell (Administrator):
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
        .\install-hermes-gateway.ps1

    Customize $distro and $wslUser variables below before running.
#>

param(
    [string]$taskName = "HermesGateway",
    [string]$distro = "Ubuntu",
    [string]$wslUser = "hermes",
    [string]$pythonCmd = "/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run"
)

Write-Host "=== Installing Hermes Gateway as Windows Scheduled Task ==="
Write-Host "Task name: $taskName"
Write-Host "Distro:    $distro"
Write-Host "User:      $wslUser"
Write-Host ""

# Stop/disable any existing systemd service (won't survive anyway)
Write-Host "Stopping any existing systemd service..."
wsl -d $distro -u root -- systemctl stop hermes-gateway 2>$null
wsl -d $distro -u root -- systemctl disable hermes-gateway 2>$null

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "wsl.exe" `
    -Argument "-d $distro -u $wslUser $pythonCmd"

$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit 0

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force

    Write-Host "✅ Task created: $taskName"
    Write-Host "   Auto-starts WSL + Gateway at Windows boot"
    Write-Host ""

    Write-Host "Starting now..."
    Start-ScheduledTask -TaskName $taskName
    Start-Sleep 3

    Write-Host "✅ Service started! Terminal closure won't affect it."
}
catch {
    Write-Host "❌ Failed: $_"
    Write-Host ""
    Write-Host "Make sure you're running as Administrator (right-click PowerShell → Run as Administrator)"
    exit 1
}

Write-Host ""
Write-Host "Management commands (Windows PowerShell Admin):"
Write-Host "  Stop:    Stop-ScheduledTask -TaskName $taskName"
Write-Host "  Start:   Start-ScheduledTask -TaskName $taskName"
Write-Host "  Status:  Get-ScheduledTask -TaskName $taskName | Get-ScheduledTaskInfo"
Write-Host "  Remove:  Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false"
