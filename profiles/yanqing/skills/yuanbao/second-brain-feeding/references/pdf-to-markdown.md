# PDF 转 Markdown 入库指南

> PyMuPDF (fitz) 是提取中文小说/书籍 PDF 文本的首选工具。无需安装 OCR，直接提取内嵌文本。

## 工具

```python
import fitz  # PyMuPDF
doc = fitz.open('book.pdf')
doc.page_count  # 总页数

# 每页提取
for i in range(doc.page_count):
    text = doc[i].get_text()
    # text 是纯文本，需自行解析章节标记
doc.close()
```

## 安装

```bash
/usr/bin/python3.14 -m pip install --break-system-packages pymupdf
```

> ⚠️ 始终用 `/usr/bin/python3.14`，不要用默认的 `python3`（uv管理的3.11在import时挂死）

## 章节检测

PDF 文本提取后，章节标题（第X章 / 上部/下部）可能因换行而中断在页面边界。检测策略：

1. 逐行扫描 `line.startswith('第') and '章' in line and len(line) < 20`
2. 关键词 `'上部'` / `'下部'` / `'前言'` / `'后记'`
3. 如果章节检测失败，不要反复重试——文本完整即可，章节标记作为二级优化

## 大规模提取（200+页，~280K字）

处理长篇小说时（如《一句顶一万句》216页, 280K字）：

### 章节检测限制
- PDF 页间换行会使「第X章」这类标题跨页断裂，导致检测结果碎片化
- 实际产出可能是「前言」+ 一大堆「第一章」「第二章」（实际是页面分段而非真正章节）
- **不要花时间精细修复**——在 frontmatter 的结构描述中用文字说明即可：
  ```yaml
  结构: 上部《出延津记》+ 下部《回延津记》
  ```
  正文用 `## 前言` / `---` 分隔即可，不做精细的 H 标签

### 内容验证
- 提取完成后务必检查**结尾几行**，确认小说结局完整（如百年孤独的「注定经受百年孤独的家族不会有第二次机会在大地上出现」）
- 检查总字数是否合理（一句顶一万句~30万字，提取~280K字合理）

### 文件大小
- 单部小说 ≈ 700-800KB, 2,000-10,000行
- 如果文件异常小（如 14KB→正文丢失），说明合并/提取出错，重新提取

### 完整提取脚本示例

```python
import fitz
doc = fitz.open('book.pdf')
total = doc.page_count

# 提取所有页
pages = []
for i in range(total):
    pages.append(doc[i].get_text())
full_text = '\n'.join(pages)

# 构建 Markdown
result = '---\n... frontmatter ...\n---\n\n' + full_text
doc.close()
```

## 文学双册结构

对于上部+下部结构的作品（如《一句顶一万句》）：

```
前 言
上部 出延津记
  ├── 第一章（多节，无显式分节）
  └── ...
下部 回延津记
  ├── 第二章（多节）
  └── ...
```

PDF 的行级提取不会保留 `<h1>/<h2>` 标记。文件结构只保留在 YAML frontmatter 的描述中。

## 已知限制

- PyMuPDF 只提取内嵌文本（selectable text），扫描版 PDF 需要 OCR
- 文字顺序可能在复杂排版下错乱（多列、图文混排）
- 制表符/空格可能被保留为特殊字符，需 `.replace()` 清理
- 章节检测对长篇小说不可靠，不追求完美
