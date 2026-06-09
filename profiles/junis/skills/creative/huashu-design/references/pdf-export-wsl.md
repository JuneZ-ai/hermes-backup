# PDF Export：无桌面环境（WSL/Headless Server）下的兜底方案

huashu-design 的标准 PDF 导出依赖 Playwright + Chromium（`scripts/export_deck_pdf.mjs`）。但在以下环境此法失效：

- **WSL2**（Ubuntu 26.04+）— Playwright 不兼容该 glibc/系统版本
- **无显示服务器的 VPS** — 未安装 Chrome/Chromium，`apt install` 需要 root
- **系统缺少中文字体** — weasyprint 因找不到 CJK font 而渲染失败

## 兜底方案：HTML → 用户浏览器 → PDF

### 工作流

```
1. 本机制作 HTML（含 @page 规则 + 分页）
       ↓ file://
2. 复制到用户桌面环境（Windows/macOS）
       ↓ 双击
3. 用户浏览器打开（Chrome / Edge）
       ↓ Ctrl+P
4. 打印对话框 → 目标：另存为 PDF
       ↓ 边距：无 · 页眉页脚：取消
5. 得到高质量矢量 PDF
```

### HTML 端的准备（本机做）

要想让 Chrome Print-to-PDF 输出接近设计品质，HTML 必须满足：

```css
/* 1. 指定纸张大小 */
@page {
  size: A4;
  margin: 0;
}

/* 2. 分页控制 */
.cover {
  page-break-after: always;
}
.page {
  page-break-after: always;
}

/* 3. 暗色背景保留（默认 print 会忽略 background） */
@media print {
  .cover {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  /* 表格/代码块深色背景同理 */
}

/* 4. 字号适配 A4（10-11pt 为阅读舒适区） */
body { font-size: 10.5pt; line-height: 1.8; }
```

### 为什么这比命令行工具好

| 对比 | 命令行（Playwright/weasyprint） | 用户浏览器 |
|:----|:-----------------------------|:----------|
| **中文字体** | 需要额外安装 Noto CJK | 系统自带（宋体/微软雅黑/PingFang） |
| **矢量保真** | 好 | **同样好**（Chrome PDF 引擎保留矢量） |
| **调试成本** | 高——每改一次 CSS 要重跑一次工具 | 低——浏览器实时预览，满意再打印 |
| **多页合并** | 需要额外脚本 | 自动完整 A4 拆分 |
| **依赖** | Playwright / weasyprint / 中文字体 | 只需用户有浏览器 |

### 覆盖的失败模式

| 症状 | 原因 | 比掉进这个坑更好 |
|:----|:-----|:---------------|
| `weasyprint` hang 到超时 | 缺少 CJK 字体 / CSS 特性阻塞 | 直接用浏览器打印 |
| `playwright` 报 Ubuntu 26.04 不支持 | Playwright browser 管理器太新 | 跳过 playwright，走兜底 |
| `chromium-headless-shell` 不存在 | 开发者没预先安装 Chrome | 不需要——用户自备 |
| PDF 中文变框框 | 系统没有中文字体 | 用户 Windows/macOS 必有 |
| 多文件 deck 页序乱 | 文件名排序与预期不符 | 单 HTML 文件天然顺序正确 |

### 使用说明（给用户）

在交付 HTML 后，附加一段话：

```
💡 **PDF 导出**
这个 HTML 已内置 A4 排版。打开后用浏览器打印（Ctrl+P）：
1. 目标打印机 → 选「另存为 PDF」
2. 更多设置 → 取消「页眉和页脚」
3. 边距 → 选「无」
4. 保存

Chrome 的 PDF 引擎保留矢量文字和色彩，效果和设计稿一致。
```
