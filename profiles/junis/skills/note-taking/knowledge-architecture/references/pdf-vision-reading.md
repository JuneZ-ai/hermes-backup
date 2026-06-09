# PDF→视觉分析阅读管线

当 PyMuPDF/mupdf 导入超时或 PDF 库卡住时，用燕青的 PDF→图片→vision_analyze 管线。

## 前置条件

- `pdf_to_images.py` 在 `~/.hermes/profiles/yanqing/pdf_to_images.py`
- 辅助视觉已配置（Qwen-VL-Max via DashScope）

## 标准流程

### Step 1：PDF 转图片

```bash
python3 ~/.hermes/profiles/yanqing/pdf_to_images.py /path/to/file.pdf --dpi 200
```

输出路径：`/home/hermes/.hermes/cache/documents/pages/同名_pNNN.png`

### Step 2：检查页数

```bash
ls /home/hermes/.hermes/cache/documents/pages/同名_p*.png | wc -l
```

### Step 3：用 vision_analyze 逐页或跳页读取

读取封面目录页了解结构：
```
vision_analyze(image_url="...p001.png", question="这是什么文档？提取目录结构")
vision_analyze(image_url="...p002.png", question="继续阅读目录")
```

读取关键章节（根据目录跳转）：
```
vision_analyze(image_url="...p003.png", question="§01 XX章节的核心内容")
```

跳页读取多个章节验证结构：
```
ls pages...p{050,070,095}.png  →  vision_analyze 确认章节位置
```

### Step 4：关键词扫描（补充）

对长文档可用 `strings` 快速扫描关键词定位：
```bash
strings /path/file.pdf | grep -i "关键词" | sort -u | head -30
```

### 适用场景

| 场景 | 原因 | 替代方案 |
|:----|:-----|:---------|
| PyMuPDF 导入超时 | Python 环境或系统负载问题 | 本管线 |
| 需看图表/排版 | vision 能保留布局信息 | PyMuPDF text 不行 |
| 99页+大文档 | 跳页策略减少 token 消耗 | 全量阅读不现实 |

### 局限

- vision_analyze 一次只看一页，逐页阅读大量页面成本高
- 图片质量依赖 dpi 设置（200 dpi 经验值）
- 中文混合英文表格可能识别不完整
