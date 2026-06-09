---
name: chrome-devtools-mcp
description: 通过 Chrome DevTools Protocol 控制 Chrome 浏览器，支持自动化、性能分析、网络监控、设备模拟
version: 1.0.0
author: Andy
tags: [browser, automation, chrome, devtools, mcp, performance, testing]
---

# Chrome DevTools MCP

通过 MCP (Model Context Protocol) 服务器控制 Chrome 浏览器，让 AI Agent 可以自动化浏览器操作、性能分析、网络监控。

## 触发场景

- 用户提到"打开浏览器"、"访问网站"、"截图"、"自动化测试"
- 用户需要性能分析、网络监控
- 用户需要录制 Demo、自动化演示
- 用户提到"Chrome DevTools"、"浏览器控制"

## 前置条件

```bash
# 安装 chrome-devtools-mcp
npm install -g chrome-devtools-mcp

# 验证安装
which chrome-devtools-mcp
```

## 核心功能

### 1. 浏览器自动化
- 导航到 URL
- 执行 JavaScript
- 点击元素
- 填写表单
- 截图

### 2. 性能分析
- 性能追踪
- CrUX 字段数据集成
- 加载时间分析

### 3. 网络监控
- 请求/响应监控
- 网络条件模拟
- Header 分析

### 4. 设备模拟
- 移动设备模拟
- 不同分辨率测试
- User-Agent 切换

## 使用方法

### 方式 1：启动新的 Chrome 实例（推荐）

```bash
# 启动一个由 MCP 控制的 Chrome 实例
chrome-devtools-mcp

# Headless 模式（无界面）
chrome-devtools-mcp --headless

# 指定视口大小
chrome-devtools-mcp --viewport 1280x720

# Slim 模式（仅 3 个核心工具：导航、JS 执行、截图）
chrome-devtools-mcp --slim
```

### 方式 2：连接到已运行的 Chrome

```bash
# 1. 先启动 Chrome 并开启远程调试
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# 2. 连接到这个实例
chrome-devtools-mcp --browserUrl http://127.0.0.1:9222

# 或使用 WebSocket 连接
chrome-devtools-mcp --wsEndpoint ws://127.0.0.1:9222/devtools/browser/abc123
```

### 方式 3：自动连接到本地 Chrome（Chrome 144+）

```bash
# 连接到正在运行的 stable Chrome
chrome-devtools-mcp --autoConnect

# 连接到 Canary 版本
chrome-devtools-mcp --autoConnect --channel=canary
```

## 配置到 Hermes Agent

在 `~/.hermes/config.yaml` 中添加：

```yaml
mcp:
  servers:
    chrome:
      command: chrome-devtools-mcp
      args: ["--headless"]
      # 或者 Slim 模式
      # args: ["--slim"]
```

配置后重启 Hermes，就可以在对话中让 AI 控制 Chrome。

## 实际应用场景

### 1. 自动化测试
```
用户：帮我测试一下 hermespet.cc 的首页加载速度
AI：启动 Chrome → 访问网站 → 性能分析 → 返回报告
```

### 2. 网页截图
```
用户：打开 GitHub trending，截图给我看
AI：启动 Chrome → 访问 GitHub → 截图 → 返回图片
```

### 3. Demo 演示
```
用户：自动演示产品的核心功能流程
AI：启动 Chrome → 按步骤操作 → 录制视频
```

### 4. 性能分析
```
用户：分析一下这个网站的性能瓶颈
AI：启动 Chrome → 性能追踪 → 分析报告
```

## 高级选项

### 禁用特定工具类别

```bash
# 禁用模拟工具
chrome-devtools-mcp --no-category-emulation

# 禁用性能工具
chrome-devtools-mcp --no-category-performance

# 禁用网络工具
chrome-devtools-mcp --no-category-network
```

### 自定义 Chrome 参数

```bash
# 添加自定义参数（谨慎使用）
chrome-devtools-mcp --chromeArg='--no-sandbox' --chromeArg='--disable-setuid-sandbox'

# 禁用默认参数
chrome-devtools-mcp --ignore-default-chrome-arg='--disable-extensions'
```

### 代理配置

```bash
# 使用代理
chrome-devtools-mcp --proxyServer http://proxy.example.com:8080
```

### 日志调试

```bash
# 保存日志到文件
chrome-devtools-mcp --logFile /tmp/chrome-devtools.log

# 启用详细日志（设置环境变量）
DEBUG=* chrome-devtools-mcp --logFile /tmp/chrome-devtools.log
```

## 安全注意事项

1. **自签名证书**：使用 `--acceptInsecureCerts` 时要谨慎
2. **沙箱**：不要轻易使用 `--no-sandbox`
3. **隐私**：使用 `--isolated` 创建临时用户数据目录
4. **网络 Header**：使用 `--redactNetworkHeaders` 隐藏敏感 header

## 实验性功能

### 1. 坐标点击（需要视觉模型）

```bash
chrome-devtools-mcp --experimentalVision
```

### 2. 屏幕录制（需要 ffmpeg）

```bash
# 安装 ffmpeg
brew install ffmpeg

# 启用屏幕录制
chrome-devtools-mcp --experimentalScreencast

# 指定 ffmpeg 路径
chrome-devtools-mcp --experimentalScreencast --experimentalFfmpegPath /usr/local/bin/ffmpeg
```

### 3. WebMCP 调试（Chrome 149+）

```bash
chrome-devtools-mcp --categoryExperimentalWebmcp
```

## 常见问题

### Q1: 如何关闭使用统计？

```bash
# 方式 1：命令行参数
chrome-devtools-mcp --no-usage-statistics

# 方式 2：环境变量
export CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1
chrome-devtools-mcp
```

### Q2: 如何使用自定义 Chrome 路径？

```bash
chrome-devtools-mcp --executablePath /path/to/chrome
```

### Q3: 如何使用自定义用户数据目录？

```bash
chrome-devtools-mcp --userDataDir /tmp/my-chrome-profile
```

## 相关资源

- [官方文档](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [promptfoo 集成](https://www.promptfoo.dev/docs/providers/)

## 版本历史

- v1.0.0 (2026-05-17): 初始版本，基于 chrome-devtools-mcp 0.26.0
