---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---
# Hermes Agent

[现有 SKILL.md 内容保持不变，在末尾添加新章节]

---

## 模型路由提示机制

在每次执行任务前，根据任务特征主动选择模型并**先给用户提示**再执行。

### 路由规则

| 任务类型 | 触发条件 | 选用模型 | 理由 |
|---------|---------|---------|------|
| 日常对话/快速响应 | 普通问题、闲聊、简单查询 | `step-3.5-flash` | 快、成本低、中文好 |
| 深度思考/推理 | 复杂分析、哲学思辨、框架设计、战略问题 | `deepseek-v4-pro` | 128K上下文、推理质量高 |
| 长文档处理 | 输入 > 2000 字、PDF/读书笔记、多轮上下文 | `deepseek-v4-flash` | 长上下文优势 |
| 代码任务 | 代码审查、编写、调试 | `step-3.5-flash` | 工具调用稳定、响应快 |
| 中文创作 | 公众号、文言文、诗词、文化内容 | `step-3.5-flash` | 中文语料质量高 |
| 视觉分析 | 图片解读、OCR辅助 | 主模型（auto fallback）| auxiliary.vision 走主模型 |
| 工具密集型 | 多工具串联（飞书+GitHub+文件）| `step-3.5-flash` | 工具适配性好 |

### 执行前提示格式

每次任务开始前（第一轮对话或任务切换时），给出简短提示：

```
【模型路由】当前任务类型：<类型> → 选用 <模型名>
```

例如：
- `【模型路由】当前任务类型：深度分析 → 选用 deepseek-v4-pro`
- `【模型路由】当前任务类型：日常对话 → 选用 step-3.5-flash`

### Fallback 规则

主模型不可用时（401/429/5xx），**自动降级并提示**：
- `step-3.5-flash` 失败 → 切换到 `deepseek-v4-flash`
- `deepseek-v4-flash` 失败 → 切换到 `step-3.5-flash`
- 两者都失败 → 提示用户检查 API 密钥

### 手动切换

用户可以通过以下指令干预：
- "用 DeepSeek" → 本次任务切到 DeepSeek
- "用 StepFun" → 本次任务切到 StepFun
- "默认用 XX" → 更新默认路由规则

### 实现参考

详见 `references/model-routing.md`。

---

## 第一性原理：只用官方API直连通道

**铁律：** 所有模型调用一律走官方API直连通道，不经任何第三方中转站（尤其是 OpenRouter）。

| Provider | 官方端点 |
|----------|---------|
| DeepSeek | `https://api.deepseek.com` |
| StepFun  | `https://api.stepfun.com/v1` |

这条规则适用于所有 bot profile 的配置。理由：第一性原理——路径越短，故障点越少，延迟越低，没有中间层挟持。

---

## 常见陷阱：模型切换路由问题

### ⚠️ `/model provider/model-name` 带前缀 → 走全局模型目录

```yaml
# ❌ 错误示范：带 provider/ 前缀
/model deepseek/deepseek-v4-flash  # ← 走 Hermes 全局模型目录 → 可能路由到 OpenRouter
```

`/model provider/model-name` 中的 `provider/` 前缀会触发 **Hermes 内置全局模型目录**查询，而不是走本地 profile 配置的 provider。例如 `deepseek/deepseek-v4-flash` 在全局目录里映射到了 OpenRouter——即使用户的 YAML 里配的是官方 `api.deepseek.com`。

### ✅ 正确做法

| 场景 | 命令 | 原理 |
|------|------|------|
| 切到当前 profile 配置的 provider | `/provider deepseek` | 直接指定用哪个 provider，继承其默认模型 |
| 在同一 provider 内换模型 | `/model deepseek-v4-flash` | 不带 `provider/` 前缀，用当前 provider 查模型 |

### 🔄 恢复出厂设置

如果模型切换后出现 `Error: Model X was not found in this provider's model listing` 或走到了错误的 provider：

```bash
/reset   # 重新加载 profile 的 model.provider 和 model.default 配置
```

### 🗑️ 清理过时的远程模型目录

默认配置会从 Hermes 官方拉取全局模型目录（`model_catalog.url`），里面包含大量过时的 provider 和模型名（如 `deepseek-reasoner`、`deepseek-chat`、Alibaba 等）。这些数据还会错误地将 `deepseek/deepseek-v4-flash` 路由到 OpenRouter。

**修复：** 在 config.yaml 中将 `model_catalog.enabled` 设为 `false`，只保留本地准确的 provider 配置。详见 `references/multi-provider-switching.md` 的「Remote model catalog」章节。

### 详细参考

完整的工作原理、配置步骤和所有 provider 列表见 `references/multi-provider-switching.md`。

---

## 多Bot模型配置指南

当需要为多个 Bot profile（如 junis、yanqing、huanglaoxie、saodiseng）配置主/备模型时：

### 配置格式

**✅ 正确格式（推荐）：**

```yaml
model:
  default: <主模型名>
  provider: <provider名>
providers:
  <provider名>:
    api_key_env: <环境变量名>
    base_url: <官方API端点>
    models: [<模型1>, <模型2>]
fallback_providers:
- provider: <备选provider名>
  models: [<备选模型>]
  activation:
    mode: sequential
    min_priority: 1
```

**❌ 过时格式（不要用）：**

```yaml
model:
  default: step-3.7-flash
  provider: stepfun
  name: step-3.7-flash          # ← 冗余，与 default 重复
  api_key_env: STEPFUN_API_KEY   # ← 应放在 providers: 块内
  api_base: https://...           # ← 应放在 providers: 块内
providers: {}                     # ← 空的，等于没配
```

过时格式的后果：`providers: {}` 导致 CLI 没有正确的 provider 定义可查，fallback 行为不可控。

### 参考配置（4-Bot标准模板）

| Bot | Profile | 主模型 | 主Provider | 备选 |
|-----|---------|--------|-----------|------|
| Hermes-Junis | junis | deepseek-v4-flash | deepseek (api.deepseek.com) | step-3.5-flash |
| 燕青 | yanqing | step-3.7-flash | stepfun (api.stepfun.com/v1) | step-3.5-flash |
| 黄老邪 | huanglaoxie | deepseek-v4-flash | deepseek (api.deepseek.com) | step-3.5-flash |
| 扫地僧 | saodiseng | deepseek-v4-flash | deepseek (api.deepseek.com) | step-3.5-flash |

**关键约束：**
- 所有模型均走直接官方API，不使用 OpenRouter 等中转
- 每个 profile 独立维护自己的 providers 块，不要依赖全局 `model_catalog`
- DeepSeek 官方API的模型名不带 `deepseek/` 前缀（`deepseek-v4-flash`，不是 `deepseek/deepseek-v4-flash`）
- 如果不用 `model_catalog` 的远程目录，将其 `enabled` 设为 `true`，但不设 `url`，只保留本地provider定义覆盖内置的 metadata
- 修改配置后各bot需执行 `/reset` + `/approve` 才能生效

---

## Skills 目录架构

Hermes Agent 加载 skills 时有**两个层级**，容易混淆：

| 层级 | 路径 | 是否被加载 | 用途 |
|------|------|-----------|------|
| **全局** | `~/.hermes/skills/` | ❌ 默认不加载 | 上游源码/第三方技能安装目标 |
| **Profile** | `~/.hermes/profiles/<profile>/skills/` | ✅ 被加载 | Hermes 实际使用的技能 |

### 如何判断当前加载的是哪个层级

看 `config.yaml` 中的 `skills.external_dirs` 配置：

```yaml
skills:
  external_dirs: []   # 空数组 = 不加载全局 skills 目录
```

当 `external_dirs: []` 时，Hermes **只读取** `~/.hermes/profiles/<profile>/skills/` 下的技能。

### 常见陷阱：升级了全局 skill 但 profile 还是旧版

这是本会话中实际踩过的坑。Darwin Skill v2.0 被复制到了 `~/.hermes/skills/`（全局），但 Hermes 读的是 `~/.hermes/profiles/junis/skills/`（profile），里面还是旧版 v1.0。升级无效。

**修复：** 手动将全局技能复制到 profile 目录：

```bash
cp ~/.hermes/skills/<skill-name>/SKILL.md ~/.hermes/profiles/<profile>/skills/<category>/<skill-name>/SKILL.md
```

或者，如果想将全局目录纳入搜索范围，在 config.yaml 中配置：

```yaml
skills:
  external_dirs:
    - /home/hermes/.hermes/skills
```

### 检查技能实际版本

```bash
head -5 ~/.hermes/profiles/<profile>/skills/<category>/<skill-name>/SKILL.md
```

对比 `~/.hermes/skills/<skill-name>/SKILL.md` 的前 5 行，确认版本号和维度数一致。

### 技能备份

修改 profile 下的技能前，建议先备份：

```bash
cp SKILL.md SKILL.md.bak.$(date +%Y%m%d-%H%M)
```

---

| 问题 | 原因 | 修复 |
|------|------|------|
| `/model` 列表有Alibaba等过时条目 | CLI二进制内置了全局模型列表 | 在 config.yaml 中重写 `model_catalog.providers` 覆盖它 |
| `/model deepseek/deepseek-v4-flash` 走到了 OpenRouter | 带 `provider/` 前缀触发了全局目录路由 | 用 `/model deepseek-v4-flash`（无前缀）或 `/provider deepseek` |
| 某个bot切到备用模型时 fallback 行为不对 | `fallback_providers` 里有多余模型名 | 确认 `fallback_providers.models` 只包含目标备选模型 |
