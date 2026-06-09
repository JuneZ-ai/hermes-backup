@echo off
:: Hermes Gateway - Windows Scheduled Task Installation (bash loop keepalive)
:: Double-click to run. Self-elevates to Administrator via UAC.
:: Does NOT require systemd — the bash loop keeps WSL alive and auto-restarts Gateway.
::
:: CUSTOMIZE: Replace hermes/Ubuntu/python-path below for your setup.

>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Administrator privileges...
    powershell Start-Process "%~s0" -Verb RunAs
    exit /b
)

cd /d %~dp0

echo.
echo === Hermes Gateway - Scheduled Task Installation ===
echo.

set WSL_USER=hermes
set WSL_DISTRO=Ubuntu
set PYTHON_CMD=/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
set BASH_LOOP=bash -c 'while true; do %PYTHON_CMD%; sleep 5; done'

:: Create the scheduled task — runs wsl.exe with bash keepalive loop at user logon
:: NOTE: /IT (interactive task) ties the process to the user session.
:: In practice, this may NOT survive CMD/PowerShell window closure.
:: For true background persistence without admin, use the VBS Startup Folder approach instead.
schtasks /CREATE ^
  /SC ONLOGON ^
  /TN "HermesGateway" ^
  /TR "wsl.exe -u %WSL_USER% -d %WSL_DISTRO% -- %BASH_LOOP%" ^
  /IT ^
  /F ^
  /RL LIMITED

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task "HermesGateway" created!
    echo.
    echo  NOTE: The /IT flag may cause termination when ALL CMD/PowerShell
    echo  windows close. Use the VBS Startup Folder approach if this happens.
    echo.
    echo  Verify with:  schtasks /Query /TN HermesGateway
) else (
    echo.
    echo [FAILED] Error code: %errorlevel%
    pause
    exit /b
)

echo.
echo Press any key to exit...
pause >nul
