' Hermes Gateway — auto-start on Windows logon
' Place this file at:
'   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\HermesGateway.vbs
'
' How it works:
' - Runs at every Windows logon (no admin needed)
' - Bash keepalive loop: keeps WSL alive, auto-restarts Gateway on crash
' - No systemd required
' - No CMD/PowerShell window needed — the VBS launches hidden (flag 0)
' - Survives CMD/PowerShell window closure — wsl.exe is held by explorer.exe
'
' CUSTOMIZE: Change -u (WSL username), -d (distro), and the python path
' to match your WSL setup.
'
CreateObject("WScript.Shell").Run "wsl.exe -u hermes -d Ubuntu -- bash -c 'while true; do /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace; sleep 5; done'", 0, False
