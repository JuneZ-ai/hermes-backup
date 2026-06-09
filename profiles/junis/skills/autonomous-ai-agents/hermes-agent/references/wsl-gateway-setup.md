# WSL 网络代理配置

> 当 WSL 无法直接访问外网（GitHub API/raw 等）时的代理方案。
> 适用于 Hermes Agent 运行在 WSL 中、Windows 上有代理工具的场景。

---

## 场景

Hermes 在 WSL 中运行时，默认可能无法直连 GitHub API（超时/403/429）。Windows 上的代理工具（如 BitZ/Clash/SS）通常能访问。

## WSL 网关 IP

WSL 的 Windows 宿主 IP 可以通过以下方式获取：

```bash
ip route | grep default | awk '{print $3}'
# 通常为 172.24.0.1 或 172.20.0.1（取决于 WSL 版本）
```

## 临时代理

```bash
WIN_IP=$(ip route | grep default | awk '{print $3}')
export http_proxy="http://$WIN_IP:7897"
export https_proxy="http://$WIN_IP:7897"
```

端口号根据 Windows 上代理工具的配置调整（BitZ 默认 7897，Clash 默认 7890）。

## 从 Python/execute_code 中使用

```python
import urllib.request
proxy = "http://172.24.0.1:7897"
handler = urllib.request.ProxyHandler({'https': proxy, 'http': proxy})
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)
```

## 前提条件

- Windows 上的代理工具必须开启 **Allow LAN**（允许局域网连接），否则 WSL 无法访问
- 代理工具端口必须对 WSL 网络开放（Windows 防火墙可能阻挡）

## 验证

```bash
curl -s --connect-timeout 5 -x http://172.24.0.1:7897 https://api.github.com/repos/mattpocock/skills
```

返回 JSON 表示代理生效。超时/Connection refused 表示代理不可达，检查 Allow LAN 设置和端口。
