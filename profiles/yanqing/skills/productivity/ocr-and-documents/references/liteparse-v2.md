# LiteParse v2 — API 参考 & 环境笔记

**Source**: [github.com/run-llama/liteparse](https://github.com/run-llama/liteparse) (LlamaIndex team)  
**PyPI**: `liteparse` v2.0.4 (2026-06)  
**License**: MIT

## 安装

```bash
pip3 install liteparse --break-system-packages
# 或
uv pip install liteparse
```

## API 类型

### `LiteParse` 构造参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `ocr_enabled` | bool\|None | True | 对扫描型页面启用 OCR |
| `ocr_server_url` | str\|None | None | HTTP OCR 服务器地址 (EasyOCR/PaddleOCR) |
| `ocr_language` | str\|None | None | Tesseract 语言 (如 "eng+chi_sim") |
| `tessdata_path` | str\|None | None | 自定义 tessdata 路径 |
| `max_pages` | int\|None | None | 限制处理页数 |
| `target_pages` | str\|None | None | 页码范围 "1-5,8" |
| `dpi` | float\|None | None | 截图 DPI |
| `output_format` | str\|None | None | 输出格式覆盖 |
| `preserve_very_small_text` | bool\|None | None | 保留极小文本 |
| `password` | str\|None | None | PDF 密码 |
| `quiet` | bool\|None | None | 静默模式 |
| `num_workers` | int\|None | None | 并行工作线程数 |

### `parse()` 方法

```python
def parse(file_data: str | pathlib.Path | bytes) -> ParseResult
```

输入：文件路径或字节数据。支持 PDF / DOCX / XLSX / PPTX / 图片。  
非 PDF 格式自动通过 LibreOffice 转 PDF 后处理。

### `ParseResult`

```python
@dataclass
class ParseResult:
    pages: list[ParsedPage]   # 每页解析结果
    text: str                 # 所有页文本拼接
```

### `ParsedPage`

```python
@dataclass
class ParsedPage:
    page_num: int             # 页码 (1-based)
    width: float              # 页宽 (points)
    height: float             # 页高 (points)
    text: str                 # 本页纯文本
    text_items: list[TextItem]  # 带位置信息的文本项
```

### `TextItem`

```python
@dataclass
class TextItem:
    text: str                 # 文本内容
    x: float                  # bbox 左上角 x
    y: float                  # bbox 左上角 y
    width: float              # bbox 宽度
    height: float             # bbox 高度
    font_name: str | None     # 字体名
    font_size: float | None   # 字号
    confidence: float | None  # OCR 置信度 (OCR 提取时)
```

### `ScreenshotResult`

类型存在（`liteparse.ScreenshotResult`），具体字段需参考源码或运行时查看。

## 使用示例

```python
from liteparse import LiteParse

# 基础用法
lp = LiteParse(quiet=True)
result = lp.parse("/path/to/document.pdf")

# 文本
print(result.text)

# 逐页文本 + 边界框
for page in result.pages:
    print(f"--- Page {page.page_num} ({page.width}x{page.height}) ---")
    for item in page.text_items:
        print(f"  [{item.x:.0f},{item.y:.0f} {item.width:.0f}x{item.height:.0f}] {item.text}")
```

## 提取管线

```
输入文件 (PDF/DOCX/XLSX/PPTX/图片)
    │
    ├─ 非 PDF → LibreOffice 自动转换 → PDF
    │
    PDF → PDFium 引擎提取原生文本 (字符级位置+字体+颜色)
    │
    ├─ 扫描型页面 → Tesseract OCR (内置, 零配置)
    │                或 HTTP OCR 服务器 (EasyOCR/PaddleOCR)
    │
    └─ 网格投影 → 虚拟字符网格 → 保留视觉布局
       (表格、多栏排版等空间结构)
    
输出 ParseResult { pages: [ParsedPage], text: str }
```

## 本环境 tessdata 问题

OCR 依赖 `tessdata` 语言数据。默认路径：

```
~/.tesseract-rs/tessdata/
```

如果该目录不存在或缺少语言文件，OCR 会报错：

```
Error opening data file .../tessdata/eng.traineddata
Failed loading language 'eng'
[ocr] failed for page N: Failed to initialize Tesseract
```

**修复**：

```bash
# 1. 安装系统包 (WSL/Ubuntu)
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim

# 2. 设置 TESSDATA_PREFIX
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# 3. 或在 LiteParse 中指定
LiteParse(tessdata_path="/usr/share/tesseract-ocr/5/tessdata")
```

**注意**：PDFium 提取原生 PDF 文本时不需要 OCR，只有扫描件页面才触发 Tesseract。如果文档是原生 PDF（带文字层），即使 tessdata 缺失也能正常提取文本。

## 性能实测 (Hermes Kanban 设计文档, 33页)

- 文本提取(PDFium): 61,216 字符 / 33 页 / 瞬时完成
- 每页 ~32 个 text_items，含完整 bbox
- 原生 PDF 无需 OCR

## 适用场景

- **RAG 系统**：结构化的 JSON 输出含 bbox，适合向量检索时融入空间特征
- **Agent 工作流**：多格式自动转换（DOCX/XLSX/PPTX → 统一 JSON）
- **布局敏感文档**：表格、多栏排版、发票、表单
- **多模态预处理**：截图生成能力可为视觉模型提供页面快照
