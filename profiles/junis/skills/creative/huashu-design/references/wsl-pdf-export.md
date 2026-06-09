# WSL 环境 PDF 导出方案

## 问题

在 WSL2 环境中（尤其 Ubuntu 26.04+），标准 PDF 导出工具可能不可用：
- **Playwright** 不支持 Ubuntu 26.04（chromium 安装失败）
- **WeasyPrint** 依赖 PIL C 扩展，系统 PIL 与 pip 安装版本冲突
- **无 sudo 权限**，无法 apt 安装 Chrome/字体
- **无中文字体**，导出 PDF 中文显示为方框

## 推荐方案：Windows Chrome 打印

最可靠的方式是将 HTML 复制到 Windows 侧，用 Chrome 导出：

### 步骤

1. 将 HTML 文件复制到 Windows 可访问的路径（如 Obsidian Vault 所在目录）
2. 在 Windows 资源管理器中双击 HTML 文件 → 默认浏览器 Chrome 打开
3. `Ctrl + P` 打开打印对话框
4. **目标打印机** → 选「另存为 PDF」
5. **更多设置** → 取消「页眉和页脚」；**边距** → 选「无」
6. 点击「保存」

### HTML 前置准备

为确保 PDF 质量，HTML 需内置以下 CSS：

```css
@page {
  size: A4;
  margin: 0;
}
@media print {
  .cover { -webkit-print-color-adjust: exact; }
  /* 深色封面保留背景色 */
}
.page {
  page-break-after: always;
}
```

### 字体

Windows 自带完整中文字体（微软雅黑、宋体等），无需额外安装。HTML 中使用系统字体即可：

```css
font-family: 'Source Han Serif SC', 'Noto Serif SC', 'Songti SC', 'SimSun', serif;
```

### 不推荐方案

| 方案 | 不推荐原因 |
|:----|:----------|
| Pandoc + wkhtmltopdf | wkhtmltopdf 需 apt 安装，无 sudo |
| WeasyPrint | PIL C 扩展兼容性问题 |
| Playwright | Ubuntu 26.04 不支持 |
| Python fpdf2/reportlab | 不支持 CSS 排版，中文字体需额外配置 |
