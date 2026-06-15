<#
.SYNOPSIS
  Hermes Agent 一键部署脚本 — 适用于全新 Win11 机器
.DESCRIPTION
  从零开始：安装 WSL2 → Ubuntu → Python → Hermes Agent → 恢复配置
  以管理员身份运行，然后去喝杯咖啡。
.NOTES
  版本: 1.0
  作者: Junis (六韬Bot团队)
#>

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$script:logFile = "$env:USERPROFILE\Desktop\hermes-deploy-log.txt"

function Write-Log {
    param([string]$Message)
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$time] $Message" | Tee-Object -FilePath $script:logFile -Append
}

# ──────────────────────────────────────────────
# 第 1 步：检查 Win11 版本
# ──────────────────────────────────────────────
Write-Log "===== Hermes Agent 一键部署 · 开始 ====="
$osInfo = Get-CimInstance Win32_OperatingSystem
$build = $osInfo.BuildNumber
$version = $osInfo.Version
Write-Log "系统: Windows $version (Build $build)"

if ([int]$build -lt 22000) {
    Write-Log "❌ 需要 Windows 11 (Build 22000+)，当前 Build $build"
    Write-Log "请升级到 Windows 11 后再试"
    exit 1
}
Write-Log "✅ Windows 11 版本满足要求"

# ──────────────────────────────────────────────
# 第 2 步：安装 WSL
# ──────────────────────────────────────────────
Write-Log "正在检查 WSL 状态..."
$wslInstalled = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslInstalled) {
    Write-Log "正在安装 WSL 功能..."
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

    Write-Log "正在下载 WSL2 Linux 内核更新包..."
    $kernelUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
    $kernelInstaller = "$env:TEMP\wsl_update_x64.msi"
    Invoke-WebRequest -Uri $kernelUrl -OutFile $kernelInstaller
    Start-Process msiexec.exe -Wait -ArgumentList "/i `"$kernelInstaller`" /quiet"

    Write-Log "设置 WSL2 为默认版本"
    wsl --set-default-version 2
} else {
    Write-Log "✅ WSL 已安装"
    wsl --set-default-version 2
}

# ──────────────────────────────────────────────
# 第 3 步：安装 Ubuntu
# ──────────────────────────────────────────────
Write-Log "正在检查 Ubuntu 发行版..."
$ubuntuInstalled = wsl -l -v | Select-String -Pattern "Ubuntu"
if (-not $ubuntuInstalled) {
    Write-Log "正在安装 Ubuntu..."
    wsl --install -d Ubuntu
    Write-Log ""
    Write-Log "⚠️  Ubuntu 首次启动需要设置 Linux 用户名和密码"
    Write-Log "   请在弹出的 Ubuntu 终端窗口中完成设置"
    Write-Log "   完成后关闭 Ubuntu 窗口，脚本自动继续"
    Write-Log "   如果未自动弹出，请手动搜索 'Ubuntu' 启动"
    Write-Log ""
    Read-Host "按 Enter 键继续（确认 Ubuntu 已设置完成）"
} else {
    Write-Log "✅ Ubuntu 已安装"
}

# 确保 Ubuntu 已启动
wsl -d Ubuntu -u root echo "WSL ready" 2>&1 | Out-Null
Write-Log "✅ WSL + Ubuntu 就绪"

# ──────────────────────────────────────────────
# 第 4 步：在 WSL Ubuntu 中安装依赖
# ──────────────────────────────────────────────
Write-Log "正在 Ubuntu 中安装系统依赖..."
wsl -d Ubuntu -u root bash -c @"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl 2>&1 | tail -1
"@

Write-Log "✅ 系统依赖安装完成"

# ──────────────────────────────────────────────
# 第 5 步：安装 Hermes Agent
# ──────────────────────────────────────────────
Write-Log "正在安装 Hermes Agent..."
wsl -d Ubuntu bash -c @"
pip3 install --user hermes-agent 2>&1 | tail -3
echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc
source ~/.bashrc
hermes --version 2>&1
"@

Write-Log "✅ Hermes Agent 安装完成"

# ──────────────────────────────────────────────
# 第 6 步：初始化 Hermes
# ──────────────────────────────────────────────
Write-Log "正在初始化 Hermes 配置..."
wsl -d Ubuntu bash -c "hermes setup init 2>&1 || true"

# ──────────────────────────────────────────────
# 第 7 步：输出完成信息
# ──────────────────────────────────────────────
Write-Log ""
Write-Log "===== 部署完成 ====="
Write-Log "Hermes Agent 已安装在 WSL Ubuntu 中"
Write-Log ""
Write-Log "下一步操作："
Write-Log "  1. 在 PowerShell 中进入 WSL：  wsl"
Write-Log "  2. 运行测试：                 hermes --version"
Write-Log "  3. 配置 API Key 和 Bot：      在飞书联系我（Junis）"
Write-Log ""
Write-Log "部署日志已保存到：$($script:logFile)"
Write-Log ""
Write-Log "如需从备份恢复完整配置，进入 WSL 后执行："
Write-Log "  git clone git@github.com:JuneZ-ai/hermes-backup.git ~/hermes-restore"
Write-Log "  cp -r ~/hermes-restore/.hermes ~/"
Write-Log ""

# 在 WSL 中创建快捷提示
wsl -d Ubuntu bash -c @"
cat > ~/HERMES_README.txt << 'EOF'
╔════════════════════════════════════╗
║   Hermes Agent 已安装             ║
║                                    ║
║   命令:   hermes                   ║
║   配置:   ~/.hermes/              ║
║   日志:   /var/log/hermes/        ║
║                                    ║
║   首次使用:                        ║
║   1. 在飞书联系 Junis 配置 Bot     ║
║   2. 或从备份恢复:                 ║
║      git clone ... ~/hermes-restore║
║      cp -r ~/hermes-restore ~/    ║
╚════════════════════════════════════╝
EOF
echo 'cat ~/HERMES_README.txt' >> ~/.bashrc
"@

Write-Log "✅ 已完成。你现在可以直接 wsl 进入 Ubuntu 使用 Hermes"
