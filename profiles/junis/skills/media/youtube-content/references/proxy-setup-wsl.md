# WSL 代理配置（YouTube/网络受限环境）

## 问题
WSL (Windows Subsystem for Linux) 默认无法直接访问 YouTube、GitHub API 等外网服务，因为代理软件只跑在 Windows 端，WSL 有自己独立的网络栈。

## 解决方案

### 1. Windows 端：开启 Allow LAN
在代理软件（BitZ/Clash/v2rayN/Shadowsocks）中找到"允许局域网连接"选项并开启。
- BitZ: 设置 → 允许局域网连接
- Clash: allow-lan: true
- v2rayN: 参数设置 → 允许来自局域网的连接

### 2. WSL 端：配置代理环境变量

```bash
# 获取 Windows 宿主机 IP（WSL 网关地址）
WIN_IP=$(ip route | grep default | awk '{print $3}')

# 设置代理（假设代理端口为 7897）
export HTTP_PROXY="http://${WIN_IP}:7897"
export HTTPS_PROXY="http://${WIN_IP}:7897"
export ALL_PROXY="socks5://${WIN_IP}:7897"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
export all_proxy="$ALL_PROXY"

# 测试代理是否可用
curl -sx "http://${WIN_IP}:7897" --connect-timeout 5 --max-time 10 \
  "https://www.youtube.com/oembed?url=https://youtube.com/watch?v=qvY0-PslC-E&format=json"
```

### 3. 常用代理端口速查
| 软件 | HTTP 端口 | SOCKS5 端口 |
|------|-----------|-------------|
| BitZ | 7897 (自定义) | 7891 |
| Clash | 7890 | 7891 |
| v2rayN | 10809 | 10808 |
| Shadowsocks | 1080 | 1080 |

### 4. yt-dlp 使用代理

```bash
yt-dlp --proxy "http://${WIN_IP}:7897" --print title "URL"
```

### 5. 持久化配置（~/.bashrc）

```bash
alias proxy-on='export WIN_IP=$(ip route | grep default | awk "{print \$3}") && \
  export HTTP_PROXY="http://${WIN_IP}:7897" && \
  export HTTPS_PROXY="http://${WIN_IP}:7897" && \
  echo "Proxy ON: ${HTTP_PROXY}"'

alias proxy-off='unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy && echo "Proxy OFF"'
```
