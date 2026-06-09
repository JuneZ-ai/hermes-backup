---
name: prompt-optimizer
description: 自动化 prompt 评估-改进循环，配合 promptfoo 使用，无框架锁定，人工在环
version: 1.0.0
author: Andy
tags: [prompt, optimization, promptfoo, llm, evaluation, automation]
---

# Prompt Optimizer

自动化 prompt 评估-改进循环。配合 [promptfoo](https://promptfoo.dev) 使用，自动识别低分 prompt 并用 LLM 重写优化。

## 触发场景

- 用户提到"优化 prompt"、"改进 prompt"、"prompt 评分低"
- 用户需要批量优化多个 prompt
- 用户提到"promptfoo"、"prompt 评估"
- 用户需要准备 Demo 演示词、投资人演讲稿

## 核心优势

| 维度 | prompt-optimizer | DSPy | Promptim |
|------|------------------|------|----------|
| **Prompt 格式** | 纯 `.txt` 文件 | DSPy signatures | LangChain templates |
| **评估系统** | 你现有的 promptfoo | 内置 | LangSmith |
| **重写 LLM** | 任何 promptfoo provider | 任何（需要 DSPy runtime） | 任何（需要 LangChain runtime） |
| **人工控制** | 每次重写前询问 | 自动 | 自动 |
| **锁定程度** | 无 | 高 | 中 |

## 前置条件

```bash
# 1. 安装 prompt-optimizer
npm install -g prompt-optimizer

# 2. 安装 promptfoo（在项目中）
npm install -D promptfoo

# 3. 设置 API Key（根据你选择的 rewriter 模型）
export OPENAI_API_KEY="sk-..."
# 或
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 工作原理

```
promptfoo eval → 解析分数 → 低于阈值？→ 用 LLM 重写 → 重新评估
                                ↓
                          全部通过 → 完成
                          停滞不前 → 停止 + 诊断
                          用户拒绝 → 停止
```

1. 运行 promptfoo 评估套件
2. 解析每个 prompt 的分数（按维度）
3. 识别低于阈值的 prompt
4. **询问是否重写**（人工在环）
5. 备份当前版本，用 LLM 重写，验证 `{{placeholders}}` 保留
6. 重新评估，重复直到全部通过或停滞

## 快速开始

### 1. 创建配置文件

在项目根目录创建 `prompt-optimizer.config.yaml`：

```yaml
# 必填：prompt 文件目录
promptsDir: prompts

# 必填：promptfoo 配置文件路径
evalConfig: evals/promptfooconfig.yaml

# 必填：版本备份目录
versionsDir: evals/prompt-versions

# 可选：环境变量文件
# envFile: .env.local

# 评分阈值（1-5 分，默认 4.0）
threshold: 4.0

# 最大迭代次数
maxIterations: 3

# 停滞阈值（最小改进幅度）
stagnationThreshold: 0.3

# 重写模型（任何 promptfoo 支持的 provider）
rewriterModel: openai:gpt-4o

# 维度映射（维度名 → rubric 中的关键词）
dimensions:
  clarity: CLARITY
  relevance: RELEVANCE
  completeness: COMPLETENESS
  actionability: ACTIONABILITY

# Provider 到文件的映射
providerToFile:
  summarizer: summarizer-system.txt
  classifier: classifier-system.txt
  responder: responder-system.txt
```

### 2. 运行优化

```bash
# 使用默认配置文件
prompt-optimizer

# 使用自定义配置文件
prompt-optimizer -c custom.yaml
```

## 配置参数详解

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| promptsDir | 是 | — | 包含 prompt `.txt` 文件的目录（支持 `{{placeholders}}`） |
| evalConfig | 是 | — | promptfoo 配置文件路径 |
| envFile | 否 | — | 环境变量文件（传递给 promptfoo 的 `--env-file`） |
| versionsDir | 是 | — | prompt 版本备份目录 |
| threshold | 否 | 4.0 | 最低可接受分数（1-5 Likert 量表） |
| maxIterations | 否 | 3 | 最大评估-改进循环次数 |
| stagnationThreshold | 否 | 0.3 | 最小改进幅度（低于此值停止） |
| rewriterModel | 否 | openai:gpt-4o | 任何 [promptfoo provider](https://www.promptfoo.dev/docs/providers/) |
| dimensions | 是 | — | `name: KEYWORD` — 关键词必须出现在 rubric 文本中 |
| providerToFile | 是 | — | `provider-label: filename` — 链接 provider 到 prompt 文件 |

## 编写高质量 Rubric

优化器的效果取决于 rubric 质量。模糊的 rubric 会产生随机分数。

### ❌ 不好的 rubric

```yaml
clarity:
  type: llm-rubric
  value: "The output should be clear."
```

**问题**：judge 会自己发明"清晰"的定义，每次运行结果不一致。

### ✅ 好的 rubric

```yaml
clarity:
  type: llm-rubric
  value: >
    CLARITY: The output uses short sentences, avoids jargon, and can be
    understood by someone with no domain expertise.
    It FAILS if the reader needs to re-read a sentence to understand it,
    or if acronyms are used without definition.
```

**改进点**：
1. 包含维度关键词（`CLARITY`）
2. 定义可观察的标准
3. 明确失败条件

### 最佳实践

#### 1. 包含维度关键词

```yaml
dimensions:
  clarity: CLARITY  # 配置文件中定义

# rubric 中必须包含 "CLARITY"
clarity:
  type: llm-rubric
  value: "CLARITY: ..."
```

#### 2. 明确定义失败条件

```yaml
relevance:
  type: llm-rubric
  value: >
    RELEVANCE: The output is specifically relevant to {{role}} in {{industry}}.
    FAILS if you could swap the industry and nothing would change.
```

#### 3. 锚定评分标准

```yaml
relevance:
  type: llm-rubric
  value: >
    RELEVANCE: The output is specifically relevant to a {{role}} working
    in {{industry}}.
    Score 5: References dynamics, risks, or terminology specific to this
    industry that would not apply elsewhere.
    Score 3: Somewhat relevant but could apply to adjacent industries
    with minor edits.
    Score 1: Generic advice that works for any industry unchanged.
    FAILS if you could swap the industry and nothing would change.
```

#### 4. 使用上下文变量

promptfoo 支持在 rubric 中使用测试变量：

```yaml
relevance:
  type: llm-rubric
  value: >
    RELEVANCE: The output is specifically relevant to {{role}} working
    in {{industry}}.
```

#### 5. 先测试 rubric

运行一次评估，阅读 judge 的推理。如果分数感觉随机，说明 rubric 太模糊。

## 实际案例

### 案例：多 prompt 流水线优化

**背景**：生产系统有 5 个链式 prompt（生成、澄清、规划、执行、综合），输出结构正确但过于通用。

**设置**：4 个维度（深度、特异性、可操作性、格式），6 个测试配置，阈值 4.0。

**优化前**：

| Prompt | 深度 | 特异性 | 可操作性 | 格式 | 平均 |
|--------|------|--------|----------|------|------|
| generation | 2.0 | 3.0 | 3.5 | 2.5 | **2.75** |
| clarification | 2.5 | 3.0 | 3.5 | 4.0 | 3.25 |
| planning | 3.5 | 3.5 | 3.5 | 4.0 | 3.62 |
| execution | 4.0 | 4.0 | 4.0 | 4.5 | 4.12 |
| synthesis | 3.5 | 4.0 | 4.0 | 4.5 | 4.0 |

**优化后（9 次迭代，约 6 小时）**：

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 最差 prompt 平均分 | 2.75 | 4.0 |
| 深度（全局） | 3.1 | 4.0 |

**关键改进**：

1. **分析前生成**（+2.0 深度）：添加"步骤 0"，强制模型先分析用户上下文
2. **跨领域深度指令**（+0.9 全局）：注入到所有 prompt："识别 3 个通才会忽略的领域特定动态"
3. **重排 JSON schema 字段**（+1.0 可操作性）：推理字段放在输出字段前，强制隐式思维链
4. **限制输出大小**（+1.5 格式）：3 个定义明确的项目 > 5 个截断的项目
5. **回归确认因果关系**：linter 回退更改后，分数降回基线，证明特定更改导致改进

**关键洞察**：上游 prompt 限制整个流水线。优化下游 prompt 无效，因为第一个 prompt 产出通用内容。

## 维度工作原理

优化器通过关键词匹配将分数映射到维度：

1. 配置文件中定义 `clarity: CLARITY`
2. rubric 文本中包含 `CLARITY`
3. promptfoo 的 judge 评估输出并分配分数
4. 优化器读取分数并映射到 `clarity` 维度

没有匹配关键词的 rubric 会被优化器忽略。

## 安全特性

1. **人工在环**：每次重写前询问
2. **版本备份**：重写前保存当前 prompt
3. **占位符验证**：拒绝丢失任何 `{{placeholder}}` 的重写
4. **停滞检测**：重写无效时自动停止
5. **无密钥存储**：从环境变量读取 API Key，不存储凭证

## 使用场景

### 1. 优化单个 prompt

```bash
cd your-project
prompt-optimizer
```

### 2. 优化 Demo 演示词

```yaml
# prompt-optimizer.config.yaml
promptsDir: demo-scripts
evalConfig: evals/demo-eval.yaml
versionsDir: evals/versions

dimensions:
  clarity: CLARITY
  relevance: RELEVANCE
  impact: IMPACT

providerToFile:
  demo-intro: demo-intro.txt
  demo-features: demo-features.txt
  demo-closing: demo-closing.txt
```

### 3. 优化投资人演讲稿

```yaml
dimensions:
  clarity: CLARITY          # 投资人能听懂
  relevance: RELEVANCE      # 针对投资人关心的点
  completeness: COMPLETENESS # 覆盖所有关键信息
  impact: IMPACT            # 展示实际价值
```

### 4. 批量优化多语言 prompt

```yaml
providerToFile:
  summarizer-en: summarizer-en.txt
  summarizer-zh: summarizer-zh.txt
  summarizer-ja: summarizer-ja.txt
```

## 平台支持

- ✅ macOS
- ✅ Linux
- ✅ WSL
- ❌ 原生 Windows（使用 WSL 或 Git Bash）

使用 `/bin/bash` 加载环境变量文件。

## 常见问题

### Q1: 如何跳过人工确认？

目前不支持。这是设计决策，防止意外覆盖 prompt。

### Q2: 如何使用不同的 rewriter 模型？

```yaml
# OpenAI
rewriterModel: openai:gpt-4o

# Anthropic
rewriterModel: anthropic:claude-3-5-sonnet-20241022

# 本地模型
rewriterModel: ollama:llama3

# 任何 promptfoo 支持的 provider
```

### Q3: 如何调试优化过程？

查看 `versionsDir` 中的备份文件，对比每次迭代的变化。

### Q4: 多个 provider 共享一个 prompt 文件怎么办？

优化器会合并它们的分数（保留每个维度的最差分数），并告诉 rewriter 平衡所有 provider 的改进。

## 相关资源

- [GitHub 仓库](https://github.com/klausners/prompt-optimizer)
- [promptfoo 文档](https://promptfoo.dev)
- [promptfoo Providers](https://www.promptfoo.dev/docs/providers/)

## 版本历史

- v1.0.0 (2026-05-17): 初始版本，基于 prompt-optimizer 0.1.0
