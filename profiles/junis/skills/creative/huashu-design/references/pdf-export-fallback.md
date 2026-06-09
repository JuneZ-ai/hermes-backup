# PDF 导出兜底方案：Chrome 打印到 PDF

## 背景

huashu-design 的 `scripts/export_deck_pdf.mjs` 依赖 Playwright + 系统 Chromium 实现矢量 PDF 导出。但在以下环境此路径不通：

| 环境 | 失败原因 |
|:----|:---------|
| **WSL2（无 sudo）** | `playwright install chromium` 失败 — Ubuntu 26.04 不在 Playwright 官方支持列表中 |
| **Linux 无 root 权限** | 无法安装 chrome/chromium 系统包 |
| **macOS 未装 Playwright** | `npm install playwright` 后需额外 `npx playwright install chromium` |
| **终端无 node/npm** | Playwright 脚本无法运行 |

## 兜底方案：HTML → Chrome 打印 → PDF

**始终有效的保底方式**，且输出质量等同于 Playwright（因为底层是同一个 Chromium 渲染引擎）：

```
HTML 文件 → 用户用 Chrome 打开 → Ctrl+P → Save as PDF
```

### 交付流程

1. **交付 HTML 文件**（已设置好 A4 打印样式）
2. **告知用户操作步骤**：
   ```
   1. 用 Chrome 打开 foo.html
   2. Ctrl+P（或 Cmd+P）
   3. 目标打印机 → 「另存为 PDF」
   4. 更多设置 → 取消「页眉和页脚」
   5. 边距 → 选「无」
   6. 保存
   ```

### HTML 需要预先具备的 CSS

在 `<style>` 中加入以下规则，确保 Chrome 打印时自动分页、保留背景色、无杂边：

```css
@page {
  size: A4;
  margin: 0;
}
@media print {
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .cover {
    page-break-after: always;
    -webkit-print-color-adjust: exact;
  }
  .page {
    page-break-after: always;
    padding: 12mm 20mm;
  }
}
```

### 与 Playwright 导出的差异

| 维度 | Playwright `page.pdf()` | Chrome Ctrl+P 打印 |
|:----|:-----------------------|:------------------|
| **文字** | 矢量（内置 Chromium 渲染） | 矢量 |
| **背景** | 精确 | 精确（需 `print-color-adjust`） |
| **自动化** | 全自动 | 需用户手动操作 |
| **可靠度** | 依赖环境 | **任何安装了 Chrome 的系统** |
| **特制尺寸** | 任意分辨率 | 标准纸张 A4/Letter 最稳 |
| **页眉页脚** | 无污染 | 默认带 URL 和页码，需手动取消 |

### 适用场景判断

| 场景 | 选哪个 |
|:----|:-------|
| 自己机器上导出 | Playwright 自动（快） |
| 交付给用户（TA 有 Chrome 但无 node） | **HTM + 打印说明**（唯一选项） |
| 服务器端批量导出 | Playwright（需提前装好 chromium） |
| CI/CD 流水线 | Playwright（需 Docker 镜像预装 chromium） |
| WSL 无 sudo / 权限不足 | **HTM + 打印说明**（兜底） |

### 中文排版注意事项

- 中文 Windows/Mac 自带宋体/黑体，HTML 中 `font-family` 需写 fallback 链：`'Noto Serif SC', 'Songti SC', 'SimSun', serif`
- 使用 `@media print` 设置的字体和字号在打印中不会变化
- Chrome 打印时默认缩放可能会影响布局，`size: A4; margin: 0` 可固定比例
