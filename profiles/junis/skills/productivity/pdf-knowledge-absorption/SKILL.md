---
name: pdf-knowledge-absorption
description: "PDF学习吸收全自动管线——PDF→图片转换→vision提取关键内容→结构化归档到飞书+Obsidian。适用于技术资料、白皮书、学术论文的知识吸收场景。"
metadata:
  requires:
    bins: ["lark-cli", "python3"]
  related:
    - reading-note-pipeline
    - lark-doc-reading-note
    - obsidian
---

# PDF学习吸收管线

## 触发条件

用户说"学习借鉴并吸纳""提取这个PDF""看看这份资料"时，且素材是PDF文件。

## 工作流

### Phase 1: PDF→图片转换

使用燕青profile的 `pdf_to_images.py` 将PDF转为PNG图片：

```bash
python3 ~/.hermes/profiles/yanqing/pdf_to_images.py /path/to/file.pdf --dpi 200
```

图片输出到 `~/.hermes/cache/documents/pages/`。

确认总页数：
```bash
ls ~/.hermes/cache/documents/pages/xxx_p*.png | wc -l
```

### Phase 2: 抓取关键章节（vision分析）

用 `vision_analyze` 读取关键页面，按优先级：

**优先级1：封面+目录页**（第1-2页）
- 提取：书名/作者/版本/章节结构
- 这是建立整体认知框架的基础

**优先级2：核心框架/导论**（通常在前15%）
- 提取：核心概念定义、方法论框架、核心理念
- 记录关键定义（用原文引用）

**优先级3：关键案例/实操**（正文重要章节）
- 提取：每个案例的核心做法和结果
- 提取：可落地的操作步骤

**优先级4：结尾/总结**（最后5-10页）
- 提取：全书结论、金句、作者观点

> ⚠️ 不要逐页通读99页PDF。按"封面→目录→框架→案例→总结"策略扫描。

### Phase 3: 结构化提取

从vision结果中，按标准格式组织：

```
书名 / 作者 / 版本
基本信息
核心框架表（支柱 | 核心内涵 | 代表篇目）
关键定义（原文引用）
重要案例（案例名 | 做法 | 结果 | 启示）
自用原则（如何应用到自己的工作方式）
```

### Phase 4: 归档到知识库

调用 `reading-note-pipeline` 的 Step 2-5 完成全流程归档：
1. 创建飞书云文档读书笔记
2. 归档到 Obsidian（DS-序号品读）
3. 更新道史总纲
4. 写搭建日志
5. 保存关键洞察到memory

### Phase 5: 内化应用（On the loop）

根据吸取的理念，评估是否应该：
- **创建/更新skill**：如果学到的方法论可以固化为可复用的工作模式
- **修改memory**：如果学到了新的工作原理/规则
- **创建模板**：如果学到了可重复使用的格式/模式
- **修改config**：如果学到了更好的环境配置方式

## 关键陷阱

1. **PDF过大**：超过50页的PDF用策略扫描而非逐页精读
2. **图片质量**：dpi=200足够文字识别，太大反而慢
3. **Python import超时**：PyMuPDF/pypdfium2在WSL下import可能很慢，先用CLI工具如 `pypdfium2 render` 或用 `pdf_to_images.py`
4. **vision识别偏差**：中英文混排、表格、代码块可能识别不完整，需要多角度补充阅读
5. **不要替用户编造**：不确定的内容（如创作时间、数据）标记为存疑或不提取
6. **优先用户提供的源文件**：如果用户给了具体版本，以该版本为准

## 示例场景

```yaml
输入: 99页技术PDF《Harness Engineering》
操作:
  1. pdf_to_images.py → 99张PNG
  2. vision读取封面(书名/作者)、目录(14章结构)、核心定义页(五组件表格)、实操页(In/On/Out of loop模型)、尾页(§18思考)
  3. 提取关键金句"不是换更聪明模型，是给同个模型更好运行环境"
  4. 创建飞书doc + 归档DS-22 + 更新总纲 + 写搭建日志 + 记入memory
  5. 自用原则: "重复3次→抽象成skill不做手工活"
输出: 完整的知识吸收闭环
```
