# 渐进式 Skill 架构：参考案例

> 本文件记录从外部优秀 skill 中汲取的架构模式，供创建新 skill 时参考。
> 当前收录：**TeachAny v7.14.1**（K12 互动课件开发 skill，作者 weponusa）

---

## TeachAny 架构分析

### 目录结构

```
teachany/
├── SKILL.md                 # 轻量执行摘要（160行，5831B）— 只留决策骨架
├── RULES.md                 # 合并后的硬规则（60行，编号 #1-#25a）
├── scripts/                 # 工具脚本
│   ├── find_nodes.py        # 按知识点查 node_id
│   ├── find-map.py          # 查历史/地理地图
│   ├── validate-courseware.cjs  # 课件质量验证
│   ├── tts-engine.py        # TTS 引擎
│   ├── gen-hero-svg.py      # 生成 Hero 知识结构图
│   └── rebuild-index.py     # 重建知识树索引
├── templates/               # 课件骨架与 manifest 模板
│   ├── course-skeleton.html
│   └── manifest-template.json
├── phases/                  # 按阶段展开的完整工作流
│   ├── workflow.md          # 4-Phase 完整流程
│   └── packaging.md         # 发布与打包流程
├── references/              # 基线规则与设计决策
│   └── baseline-rules.md    # 19项基线规则
├── guides/                  # 使用指南
│   ├── pbl.md               # PBL 项目式学习设计
│   ├── assessment.md        # 评估设计
│   └── interactive-templates.md  # 互动示例
├── tech/                    # 技术实现细节
│   ├── page-structure.md    # 页面结构规范
│   ├── design.md            # 设计指南
│   └── math-science-sim.md  # 数学/科学仿真
└── topics/                  # 专题文档
    └── maps-and-3d.md       # 地图与3D
```

### 关键设计决策

#### 1. SKILL.md 是「决策骨架」而非「操作手册」

```markdown
# TeachAny：K12 互动课件执行摘要

TeachAny 的目标不是把知识堆进页面，而是把一节课做成
有问题锚点、有互动、有讲解、有评估、有发布闭环的学习体验。

主文件只保留决策骨架；细节按需读取卫星文档。
```

SKILL.md 只放：
- 何时使用（触发条件 + 反例）
- Quick Start（一条完整路径的示例）
- 核心原则（「没有快速模式」等）
- 4-Phase 流程总览（每个阶段1-2行摘要 + 链接到 `phases/` 中的完整文档）
- 核心规则（最终有效版，每条 1-2 行）

不放：
- 完整工作流步骤 → 放 `phases/workflow.md`
- API 参数表格 → 放 `tech/page-structure.md`
- 设计指南 → 放 `guides/`
- 脚本用法 → 放 `scripts/` 的 --help 或 README

#### 2. RULES.md 是「可执行的纪律」

每条规则：
- **有编号**（#1, #2, ...）→ 对话中可以精准引用
- **可验证** → 不是「要注意质量」，是「声称完成前必须跑验证脚本」
- **有条件** →「失败两次换方案」「一类问题一起扫」

```
# TeachAny 硬规则（合并最终版）

## A. 执行纪律
- #1 闭环验证：声称完成/修复前必须运行实际命令或浏览器验证
- #2 事实驱动：定位原因前先 grep/read/curl，不做无证据归因
- #3 失败两次换方案：同一方向连续失败 2 次，切换本质不同路径
```

#### 3. 「没有快速模式」原则

> 所有课件必须完整包含 19 项基线。没有"快速模式"。
> 唯一允许豁免的情形：外部资源确实不可达。

这条原则解决了 agent 最常见的偷懒行为——「先做一个简版，之后再补」（实际上永远不会补）。

#### 4. 卫星文档的职责拆分

| 目录 | 职责 | 不适合放什么 |
|------|------|-------------|
| `phases/` | 顺序执行的工作流步骤 | 背景知识、设计哲学 |
| `references/` | 基线规则、检查清单 | 可执行步骤 |
| `guides/` | 设计指南、最佳实践 | 硬性规则 |
| `tech/` | 技术实现、API 参考 | 流程步骤 |
| `templates/` | 可复用的文件骨架 | 文档说明 |
| `scripts/` | 可执行的工具脚本 | 文档 |

---

## 如何应用到 Hermes Skill

### Hermes 版最小渐进式结构

```
skills/<category>/<name>/
├── SKILL.md              # 决策骨架（必需）
├── RULES.md              # 硬规则（可选，推荐有不可违反规则时）
├── references/           # 参考文档（可选）
│   ├── baseline.md       # 基线规则
│   └── api.md            # API 参考
└── templates/            # 模板文件（可选）
    └── example-config.yaml
```

### Hermes 版 RULES.md 模板

```markdown
# <Skill Name> 硬规则

## A. 执行纪律

- **#1** **闭环验证**：声称完成前必须运行验证命令并给出输出。
- **#2** **事实驱动**：定位问题前先读文件/查日志，不做无证据归因。
- **#3** **失败两次换方案**：同一方向连续失败 2 次，切换路径。
- **#4** **一类问题一起扫**：修一处后检查是否别处有同类问题。

## B. 内容规范

- **#5** [具体规则]
- **#6** [具体规则]

## C. 红线

- **#7** [不可违反的底线]
```

---

*参考来源：TeachAny v7.14.1 by weponusa (https://github.com/weponusa/teachany)*
