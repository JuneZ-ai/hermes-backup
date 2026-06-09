---
name: textual-alchemist
display_name: 文渊匠 (Textual Alchemist)
description: 文渊匠——全品类文档高精度数字化与结构化专家。古籍管线（校勘/竖排OCR/知识图谱/置信度评分），现代文档管线（扫描杂志/报告→深度阅读笔记），Obsidian知识库集成。Hermes/WSL 适配版。
version: 3.3.0
author: 异虎事业部 → Hermes
tags: [古籍, 数字化, OCR, 结构化, 校勘, 知识图谱, 竖排文字, 现代文档, 深度阅读, Obsidian]
trigger_words: 古籍数字化、古籍OCR、古籍转JSON、文渊匠、textual-alchemist、古籍校勘、版本对比、竖排OCR、深度阅读笔记、文档处理、扫描PDF
---

# 文渊匠 (Textual Alchemist)
## 全品类文档高精度数字化与结构化专家 — Hermes/WSL 版 v3.3

> 基于 WorkBuddy 原版 v3.2.0（2026-05-24）适配 Hermes Agent / WSL 环境。
> 核心方法论和管线不变，工具链从 Windows 移植到 Linux/WSL。

---

## 📥 标准化输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|:----:|:----:|------|
| `source.type` | string | ✅ | 输入类型：`pdf` / `text` / `image` |
| `source.path` | string | ✅ | 文件路径 |
| `options.book_title` | string | ❌ | 文档名称（留空自动识别） |
| `options.chapters` | string | ❌ | 章节范围，如 `"第1章-第5章"` 或 `"全部"`，默认全部 |
| `options.mode` | string | ❌ | 处理模式：`precision`(含语义校核) / `quick`(仅清洗+结构化) / `digest`(深度阅读笔记)，默认 `precision` |
| `options.doc_category` | string | ❌ | 文档分类：`classical`(古籍) / `modern`(现代文档) / `textbook`(教材) / `auto`(自动检测)，默认 `auto` |
| `options.collation` | string | ❌ | 版本校勘模式 `off` / `auto` / `multi`，默认 `off` |
| `options.collation_sources` | array | ❌ | 校勘用多版本文件路径数组 |
| `options.output_format` | string | ❌ | 输出格式：`json` / `jsonl` / `markdown` / `deep_reading_notes`，默认 `json` |
| `options.include_annotations` | boolean | ❌ | 是否提取注疏，默认 `true` |
| `options.include_modern_translation` | boolean | ❌ | 是否生成白话翻译，默认 `true` |
| `options.ocr_dpi` | integer/string | ❌ | OCR分辨率，默认 `"auto"`（自动选择）|
| `options.ocr_lang` | string | ❌ | OCR语言包，默认 `chi_sim` |
| `options.vertical_text` | boolean | ❌ | 是否为竖排古籍，默认 `auto` |
| `options.quality_threshold` | number | ❌ | 置信度阈值(0-1)，默认 `0.85` |
| `options.obsidian_integration` | boolean | ❌ | 是否自动集成到Obsidian知识库，默认 `false` |

---

## 📤 标准化输出参数

| 参数 | 类型 | 说明 |
|------|:----:|------|
| `book_title` | string | 文档名称 |
| `chapter_id` | string | 章节序号 |
| `chapter_title` | string | 章节名称 |
| `content_nodes[].node_id` | integer | 节点序号 |
| `content_nodes[].original_raw` | string | 清洗前原始文本 |
| `content_nodes[].cleaned_text` | string | 清洗后纯净文本 |
| `content_nodes[].annotations` | array | 注解数组 |
| `content_nodes[].modern_translation` | string | 现代翻译 |
| `data_integrity.processing_status` | string | `SUCCESS` / `PARTIAL` / `FAILED` |

**digest 模式额外输出：**
| 参数 | 说明 |
|------|------|
| `reading_notes.core_summary` | 200字核心摘要 |
| `reading_notes.chapter_insights[]` | 逐章深度解读 |
| `reading_notes.cross_domain_insights[]` | 跨领域洞察 |
| `reading_notes.action_items[]` | 行动建议 |
| `reading_notes.golden_quotes[]` | 金句摘录 |
| `obsidian_integration.files_created[]` | Obsidian文件列表 |
| `processing_stats.total_time_seconds` | 总耗时 |
| `processing_stats.pages_per_second` | 处理速度（页/秒）|

---

## 〇、文档分类路由（首步必读）

在处理任何文档之前，必须先判定文档类型，选择正确的处理管线。

```
输入文件 → 格式检测 → 文档分类路由 ─┬→ [classical] 古籍管线
                                    │   OCR → 符号纠错 → 注疏分离 → JSON结构化
                                    ├→ [modern] 现代文档管线
                                    │   OCR → 章节检测 → 要点提炼 → 深度阅读笔记
                                    └→ [textbook] 教材管线
                                        OCR → 标题树 → JSON结构化 → 模块化存储
```

### 自动分类算法

```python
import re

def classify_document(text_sample, file_path=None):
    """基于文本采样自动判定文档类型"""
    classical_markers = [
        r'[經传子集卦爻卷篇章]', r'[曰云注解疏]',
        r'[元亨利贞吉凶悔吝]', r'^[上下內外][篇]',
    ]
    modern_markers = [
        r'(封面文章|特写|行业洞察|编者按|卷首语)',
        r'(大数据|人工智能|数字化转型)',
    ]
    textbook_markers = [
        r'(第[一二三四五六七八九十\d]+章)',
        r'(思考题|课后习题|本章小结|学习目标)',
    ]

    def score(markers):
        return sum(1 for m in markers if re.search(m, text_sample))

    return max(
        [('classical', score(classical_markers)),
         ('modern', score(modern_markers)),
         ('textbook', score(textbook_markers))],
        key=lambda x: x[1]
    )[0]
```

---

## 一、核心工作流

### 步骤1：PDF类型检测

```python
import fitz  # PyMuPDF

def detect_pdf_type(path):
    """检测PDF是文本型还是扫描型"""
    doc = fitz.open(path)
    text_lens = [len(doc[i].get_text()) for i in range(min(3, len(doc)))]
    doc.close()
    avg_chars = sum(text_lens) / len(text_lens) if text_lens else 0
    return 'text' if avg_chars > 50 else 'scan'
```

- **文本型PDF**（avg_chars > 50/页）：直接 `page.get_text()` 提取
- **扫描型PDF**（avg_chars <= 50/页）：转图片 → Tesseract OCR

### 步骤2：OCR（仅扫描型PDF）

```python
from PIL import Image
import pytesseract

# Tesseract路径在Hermes/WSL中已由 hermes-ocr 包装器处理
# pytesseract 会自动使用系统路径（hermes-ocr 设了 LD_LIBRARY_PATH）
pytesseract.pytesseract.tesseract_cmd = '/home/hermes/.local/bin/hermes-ocr'

def ocr_page(image_path, dpi=150, lang='chi_sim'):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang, config=f'--dpi {dpi} --psm 6')
    return clean_ocr_text(text)
```

### 步骤3：后处理清洗

```python
def clean_ocr_text(raw_text):
    """清洗Tesseract中文OCR常见问题"""
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', raw_text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=\d)', '', text)
    text = re.sub(r'(?<=\d)\s+(?=[\u4e00-\u9fff])', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace(' 。', '。').replace(' ，', '，').replace(' 、', '、')
    return text.strip()
```

### 步骤4：结构化输出（根据文档类型）

分类处理后，输出统一的 JSON 结构：

```json
{
  "book_title": "文档名称",
  "chapter_id": "章节序号",
  "chapter_title": "章节名称",
  "content_nodes": [
    {
      "node_id": 1,
      "original_raw": "清洗前的原始文本",
      "cleaned_text": "清洗后的纯净文本",
      "annotations": [{"author": "注者", "text": "注解文本"}],
      "modern_translation": "现代白话文翻译"
    }
  ],
  "data_integrity": {
    "garbled_char_count": 0,
    "processing_status": "SUCCESS"
  }
}
```

---

## 二、古籍管线（classical）

### 2.1 符号纠错

常见 OCR 错误映射（易经专用示例）：

| 错误 | 正确 | 说明 |
|------|------|------|
| 衆 | 卦 | "卦"误识别为"衆" |
| 結 | 六 | "六"识别为"結" |
| モ | 上 | "上"识别为片假名 |
| 阿 | 五 | "五"识别为"阿" |
| 惇 | 四 | "四"识别为"惇" |
| k | 《 | 书名号左半边 |
| 3 | 》 | 书名号右半边 |

### 2.2 注疏分离

古籍通常包含"经/原文"与"后人注解"，必须将两者彻底解耦：

| 类型 | 说明 |
|------|------|
| **Original Text (经/原文)** | 核心经典文本 |
| **Commentary (注疏/注解)** | 后人对该句的阐释，需标注作者 |

注解者标注规范：王弼 / 河上公 / 朱熹 / 孔颖达 / 程颐 / 王阳明 等。如未知，填写 **"集注"**。

### 2.3 竖排文字处理

Tesseract 仅支持横排文字。竖排古籍的解决方案：
1. 将图片旋转 90° 或 270° 后再 OCR
2. OCR 后按原方向重组文字顺序
3. 保留古籍原有的异体字与通假字，不盲目简化

### 2.4 版本校勘

当提供多版本时（`options.collation='multi'` + `collation_sources`），对比不同版本的文本差异，输出校勘表。

---

## 三、现代文档管线（modern）

### 3.1 适用文档类型

| 类型 | 示例 |
|------|------|
| 商业杂志/期刊 | 埃森哲《展望》、哈佛商业评论 |
| 行业报告/白皮书 | 麦肯锡报告、Gartner分析 |
| 会议论文集 | 学术会议论文集 |
| 企业内刊 | 公司年报、内部杂志 |

### 3.2 章节自动检测

```python
def detect_modern_chapters(ocr_text_by_page):
    """检测杂志/报告的章节结构"""
    chapters = []
    for page_num, text in ocr_text_by_page.items():
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if not line or len(line) > 30:
                continue
            # 模式1: "标题：副标题"
            if '：' in line or ':' in line:
                chapters.append((line, page_num))
                break
            # 模式2: 栏目关键词
            if any(kw in line for kw in ['封面文章', '特写', '行业洞察', '访谈', '卷首', '编者']):
                chapters.append((line, page_num))
                break
            # 模式3: 独立短行（3-20字）
            if 3 <= len(line) <= 20 and page_num > 3:
                chapters.append((line, page_num))
                break
    return chapters
```

### 3.3 深度阅读笔记生成（digest模式）

```
OCR全文 → 章节检测 → 核心摘要(200字) → 逐章要点提炼 →
跨章节洞察 → 与用户知识体系关联 → 行动建议 → 金句摘录
```

输出结构：

| 模块 | 内容 | 字数 |
|------|------|:--:|
| 元数据 | 标题/作者/出版信息/标签 | — |
| 核心摘要 | 一句话概括 + 200字摘要 | ~200 |
| 章节地图 | 全部章节标题+页码范围 | — |
| 逐章深度解读 | 每章3-5个要点 + 1句洞察 | 每章~150 |
| 跨领域洞察 | 2-3个跨章节/跨行业发现 | ~300 |
| 与知识体系关联 | 与用户关注领域的链接点 | ~200 |
| 行动建议 | 3-5条可执行建议 | ~150 |
| 金句摘录 | 5-10条原话引用 | — |

---

## 四、教材管线（textbook）

### 4.1 适用文档

- 大学教材/教科书
- 职业培训教材
- 学术专著

### 4.2 教材处理策略

教材关键特征是有层级明确的标题树（章→节→小节）和习题/思考题。

处理流程：
1. OCR 全文（如为扫描型）
2. 检测标题层级：`第X章` → `第X节` → `一、二、三、` → 子标题
3. 按章节模块化存储

---

## 五、Obsidian集成

### 5.1 Vault路径

```
Hermes/WSL: /mnt/d/Obsidian/异虎事业部知识库/
```

通过 `options.obsidian_integration=true` 启用。使用 Hermes 的 `obsidian` skill 中的 `write_file` 创建笔记。

### 5.2 文件分发策略

| 输出类型 | 目标目录 |
|---------|---------|
| 深度阅读笔记 | `07-学习笔记/` |
| 行业洞察引用 | `03-行业洞察/行业趋势/` |
| 知识体系关联 | `六韬易哲/` 或用户指定 |
| MOC更新 | `09-MOC/MOC-行业洞察.md` 添加双链 |

### 5.3 Obsidian格式输出模板

```markdown
---
title: "{book_title}"
tags:
  - {category}
  - 行业洞察
created: {date}
source: "{file_path}"
---

## 📌 核心摘要

{core_summary}

## 🗺️ 章节地图

| 章节 | 页码范围 | 核心主题 |
|------|---------|---------|
{chapter_map}

## 📖 逐章深度解读

{chapter_insights}

## 🔍 跨领域洞察

{cross_domain_insights}

## ✅ 行动建议

{action_items}

## 💬 金句摘录

{golden_quotes}

---

*文档来源：{source} | 总页数：{total_pages} | 处理耗时：{time}*
```

---

## 六、Hermes/WSL 运行环境

### 6.1 已安装工具

| 工具 | 版本 | 用途 | 备注 |
|------|------|------|------|
| Python | 3.14.4 | 脚本引擎 | 系统Python |
| Tesseract OCR | 5.5.0 | OCR引擎(chi_sim) | 通过 `hermes-ocr` 包装器调用 |
| PyMuPDF (fitz) | 1.27.2.3 | PDF解析、图片提取 | 同时替代 pdftotext/pdfplumber |
| Pillow | 12.2.0 | 图片预处理 | |
| pytesseract | 0.3.13 | Python→Tesseract桥接 | |

### 6.2 OCR速度优化矩阵

| DPI | 近似尺寸 | 单页耗时 | 100页耗时 | 推荐场景 |
|-----|:---:|:---:|:---:|------|
| 100 | ~667×1003 | ~2.0s | ~3.3min | 纯文本、现代文档>50页 |
| **150** | **~1000×1505** | **~3.3s** | **~5.5min** | **出厂默认——速度质量最佳平衡** |
| 200 | ~1333×2007 | ~5.5s | ~9min | 古籍、小字体、高精度 |

```python
def auto_select_dpi(total_pages, doc_category='modern'):
    if doc_category == 'modern':
        return 100 if total_pages > 50 else 150
    elif doc_category == 'textbook':
        return 150
    elif doc_category == 'classical':
        return 200
    return 150
```

### 6.3 PDF图片提取

```python
import fitz

def pdf_to_images(pdf_path, output_dir, dpi=150):
    """将PDF每页转为PNG图片"""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72, dpi/72)  # 默认72dpi
        pix = page.get_pixmap(matrix=mat)
        out_path = f"{output_dir}/page_{page_num+1:04d}.png"
        pix.save(out_path)
        images.append(out_path)
    doc.close()
    return images
```

### 6.4 并行策略（Linux优势）

**Linux 下 multiprocessing 可用（与 Windows 不同）：**

```python
from multiprocessing import Pool
from functools import partial

def batch_ocr(pages, lang='chi_sim', dpi=150, n_workers=4):
    """Linux下可用多进程并行OCR"""
    with Pool(n_workers) as pool:
        results = pool.map(process_page, pages)
    return results
```

**建议：**
| 页数 | 策略 |
|------|------|
| < 20页 | 单进程 |
| 20-100页 | 4进程并行 |
| 100-500页 | 4进程 + 每20页保存检查点 |
| > 500页 | 4进程 + 检查点 + 断点续传 |

---

## 七、Hermes/WSL 避坑指南

### 7.1 Tesseract必须在hermes-ocr包装器下运行

```python
# ❌ 错误：直接调用 tesseract
# subprocess.run(['tesseract', ...])  # 找不到libtesseract.so.5

# ✅ 正确：使用 hermes-ocr 包装器
pytesseract.pytesseract.tesseract_cmd = '/home/hermes/.local/bin/hermes-ocr'
```

### 7.2 中文OCR配置

```python
# hermes-ocr --list-langs 确认只有 chi_sim
# 没有 chi_sim_vert（竖排语言包）
# 竖排古籍需旋转图片后使用 chi_sim
```

### 7.3 PyMuPDF作为全能PDF工具

WSL 无 pdftotext/poppler-utils，PyMuPDF 一应俱全：
- 文本提取：`page.get_text()`
- 图片提取：`page.get_pixmap()`
- 页面计数：`len(doc)`
- 元数据：`doc.metadata`

```python
import fitz
doc = fitz.open(path)
# 文本型PDF检测
avg_chars = sum(len(doc[i].get_text()) for i in range(min(3, len(doc)))) / min(3, len(doc))
```

### 7.4 pdfplumber不可用

WSL 未安装 pdfplumber。所有表格提取等操作使用 PyMuPDF 或 Python 正则处理。

### 7.5 文件路径格式

```python
# ✅ WSL正确路径
path = '/mnt/d/Obsidian/异虎事业部知识库/07-学习笔记/xxx.md'

# ❌ Windows路径不可用（除非在/mnt/c/下）
# path = 'D:\\Obsidian\\...'  # 不工作
```

### 7.6 大文件处理

```python
def ocr_with_checkpoint(pages, checkpoint_file, page_size=20):
    """带检查点的大文件OCR"""
    processed = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            processed = set(int(line) for line in f)

    results = {}
    for i, page in enumerate(pages):
        if i in processed:
            continue
        try:
            text = ocr_page(page)
            results[i] = text
        except Exception as e:
            results[i] = f"[OCR_ERROR] {e}"
        # 每处理 page_size 页保存检查点
        if (i + 1) % page_size == 0:
            with open(checkpoint_file, 'w') as f:
                for p in processed | set(results.keys()):
                    f.write(f"{p}\n")
    return results
```

---

## 八、交付标准

1. JSON 文件可直接被 `json.loads()` 解析
2. 所有字符串内双引号已正确转义
3. 无 Markdown 代码块包裹
4. 文件编码为 UTF-8
5. digest 模式输出含完整的阅读笔记结构
6. obsidian 模式下 create/update 操作均有日志可追溯

---

## 九、知识库来源

- 易经根基：曾仕强《易经真的很容易》69节课程
- 八字经典：渊海子平、子平真诠、滴天髓、三命通会、千里命稿
- 相学经典：麻衣神相、柳庄相法、冰鉴、铁关刀
- 道德经注：河上公注、王弼注、朱熹注
- 论语注：何晏集解、朱熹集注

---

## 十、经验来源

| 任务 | 文档类型 | 规模 | 关键经验 |
|------|---------|:---:|---------|
| 埃森哲《展望》AI专刊 | 扫描PDF（现代杂志） | 117页 | DPI选择、章节检测、阅读笔记 |
| 中医诊断学第5版 | DOCX（教材） | 313段/25K字 | 标题树提取、模块化存储 |
| 金匮要略 | PDF+DOCX | 中 | 繁简转换、注疏分离 |
| 伤寒论倪海厦注 | DOCX | 274K字 | 大文件处理、繁简转换 |
| 倪海厦天纪三书 | 文本PDF | 多卷 | 文本提取、Obsidian批量集成 |
| Tesseract环境搭建 | — | — | WSL环境适配、LD_LIBRARY_PATH |

---

*技能版本：v3.3.0 | Hermes/WSL 适配版 | 基底：v3.2.0 (异虎事业部)*
