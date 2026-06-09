# RapidOCR 长截图中文提取（喂料流水线场景）

## 用途

当用户发的视频号/公众号内容是**长截图**（而非可提取HTML的链接），且当前模型不支持视觉时，用 RapidOCR 本地提取中文文案。

## 前置条件

```bash
pip install rapidocr-onnxruntime pillow
```

约150MB（含 ONNX Runtime + 中文字符识别模型），无需 sudo。

## 注意：RapidOCR 结果格式

```python
result, elapse = engine(image_path)   # 返回元组
# result = [(bbox, text, confidence), ...]  ← 真正的内容在这里
# elapse = 时间统计
```

**不要直接迭代 `engine()` 的返回值**——它是 `(detections, timing)` 元组。始终取 `result[0]`（或上面的解包方式）。

## 大图分块处理（929×11822px 级别）

RapidOCR 比 PaddleOCR 更轻量，单实例可复用，内存约 200-300MB。但超大图仍需分块：

```python
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

# 1. 分块
img = Image.open("screenshot.jpg")
w, h = img.size
n = h // 2000 + 1
for i in range(n):
    y1, y2 = i * 2000, min((i+1) * 2000, h)
    img.crop((0, y1, w, y2)).save(f"chunk_{i}.jpg")

# 2. 逐块OCR
engine = RapidOCR()
all_text = []
for i in range(n):
    result, _ = engine(f"chunk_{i}.jpg")
    if result:
        texts = [text for _, text, conf in result if conf >= 0.5]
        all_text.extend(texts)

# 3. 保存
with open("result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_text))
```

## 置信度阈值指南

| 阈值 | 适用场景 | 说明 |
|:----:|:--------|:----|
| 0.5 | 标准文章/正式文本 | 干净结果，偶有漏字 |
| 0.3 | 界面截图/花体字 | 保留更多，噪声略多 |
| 0.7 | 印刷体+纯白背景 | 最干净，可能漏小字 |

建议先用 0.5 跑一轮，如果发现缺失内容较多再降至 0.3。

## 已知局限

- 对于竖排文字（书法/古籍）支持不佳
- 对于极小字号（<10px）或极低对比度文字可能漏识
- 对于特殊字体（楷体/行书手写）质量下降
- 不适用于繁体/日文（需额外语言模型，下载可能受阻）

## 参考

完整方案及备选方案见 `ocr-and-documents` 技能（含 PaddleOCR、Tesseract、marker-pdf 等对比）。
