---
name: huashu-nuwa
description: |
  女娲造人：输入人名/主题/甚至只是模糊需求，自动深度调研→思维框架提炼→生成可运行的人物Skill。
  两种入口：(1)明确人名→直接蒸馏 (2)模糊需求→诊断推荐→再蒸馏。
  触发词：「造skill」「蒸馏XX」「女娲」「造人」「XX的思维方式」「做个XX视角」「更新XX的skill」。
  模糊需求也触发：「我想提升决策质量」「有没有一种思维方式能帮我...」「我需要一个思维顾问」。
---

# 女娲 · Skill造人术（Hermes版）

> 提炼一个人的思维框架，而非复制这个人。

完整版见 WorkBuddy：`/mnt/c/Users/18502/.workbuddy/skills/huashu-nuwa/SKILL.md`（644行，33KB）
回退蒸馏案例：`references/bret-taylor-distillation-20260524.md` — 2026-05-24 通过 Hermes 复刻女娲流程成功蒸馏 Bret Taylor 技能的完整记录（含6份调研+17KB SKILL.md）
示例产出：`/mnt/c/Users/18502/.workbuddy/skills/huashu-nuwa/examples/`（13个perspective skill）

---

## 核心理念

一个好的人物Skill是一套可运行的认知操作系统：
- **心智模型** — 他用什么镜片看世界？
- **决策启发式** — 他的直觉规则是什么？
- **表达DNA** — 他的话语风格？
- **反模式** — 他绝对不会做什么？
- **诚实边界** — 这个Skill做不到什么？

关键：捕捉 **HOW they think**，不是 **WHAT they said**。

---

## 执行流程

### Phase 0: 入口分流

| 输入 | 路径 |
|------|------|
| 明确人名/主题 | **直接路径** → 确认人物、聚焦方向、用途、新建or更新 |
| 模糊需求/困惑 | **诊断路径** → 定位需求维度 → 推荐2-3候选 → 用户选择 |

**⚠️ 用户偏好：启动前先报预期时间**
在执行多步骤复杂任务前（特别是启动6个并行agent前），必须提前告知用户：
- 总耗时预估（如"约8-12分钟"）
- 分阶段说明（Phase 1 ~5min → Phase 2-3 ~3min → Phase 4 ~1min）
- 不要让用户干等无反馈。如果因用户中断导致任务重来，需重新报时。

成功案例参考：
- `references/bret-taylor-distillation-20260524.md` — Bret Taylor 蒸馏（Hermes 回退模式，纯训练知识完成）
- `references/duanyongping-distillation-20260526.md` — 段永平蒸馏（6调研+24KB SKILL.md，Hermes 直接执行，含0代码用户交互）

### Phase 0.5: 创建Skill目录

```
~/.hermes/skills/[person-name]-perspective/
├── SKILL.md                          # 最终产物
├── references/
│   └── research/                     # 6个Agent调研结果
│       ├── 01-writings.md            # 著作与系统思考
│       ├── 02-conversations.md       # 长对话与即兴思考
│       ├── 03-expression-dna.md      # 碎片表达与风格DNA
│       ├── 04-external-views.md      # 他者视角与批评
│       ├── 05-decisions.md           # 决策记录与行动
│       └── 06-timeline.md            # 人物时间线
```

### Phase 1: 多源信息采集（并行Agent Swarm）

启动**6个并行 subagent**，每个负责不同维度：

> **⚠️ 网络受限时的调研回退策略**
> 当 subagent 无法联网（如 WSL 环境无 WebSearch 工具）时，不要阻塞：
> 1. 用 `curl` 抓取目标人物的主要公开页面（公司官网 bio、Wikipedia 等）
> 2. 结合自身训练知识中的事实信息（标注「推断」而非「一手」）
> 3. 按六维框架逐项填写，在每份调研文件头部标注数据来源限制
> 4. **绝不编造来源** — 信息不足的维度诚实标注「信息不足，此维度为推测」
>
> 成功案例：2026-05-24 Bret Taylor 蒸馏（Hermes 回退模式）— 纯靠 Sierra.ai 页面 + 训练知识完成 6 份调研 + 17KB SKILL.md，质量自检全部通过。

| Agent | 搜索目标 | 输出文件 |
|-------|---------|---------|
| 1 著作 | 书、长文、论文、newsletter | `01-writings.md` |
| 2 对话 | 播客、长视频、AMA、深度采访 | `02-conversations.md` |
| 3 表达 | X/Twitter、微博、短文 | `03-expression-dna.md` |
| 4 他者 | 他人分析、书评、批评、传记 | `04-external-views.md` |
| 5 决策 | 重大决策、转折点、争议行为 | `05-decisions.md` |
| 6 时间线 | 完整时间线，含最近12个月 | `06-timeline.md` |

**硬性要求**：
- 调研结果写入 `references/research/0X-xxx.md`
- 注明信息来源和可信度（一手 > 二手 > 推测）
- 区分「他说过的」vs「别人说他的」vs「我推断的」
- 发现矛盾时保留矛盾，不要和稀泥
- 信息源黑名单：知乎、微信公众号、百度百科

### Phase 2: 思维框架提炼

从6份调研中提取：
1. **核心心智模型**（3-5个，每个阐述清楚）
2. **决策启发式**（即兴规则，至少5条）
3. **表达模式**（高频词、句式、语气）
4. **反模式**（此人绝对不做什么）
5. **知道与不知道的边界**（诚实标注局限性）

### Phase 3: SKILL.md 合成

按标准Skill格式撰写：
- YAML frontmatter + 含触发词的description
- 核心心智模型作为一级section
- 决策启发式作为清单
- 反模式作为警告
- **必须包含局限性说明** — 什么场景不适合用此思维框架

### Phase 4: 质量自检（参考WB版quality_check.py）

- [ ] 心智模型数 ≥ 3
- [ ] 有明确的局限性说明
- [ ] 表达DNA可识别（有具体句式示例）
- [ ] 有诚实边界（知道与不知道）
- [ ] 保留内在张力（矛盾观点不做调和）
- [ ] 一手来源占比 > 50%

---

## WorkBuddy 400错误处理

当通过WB调用女娲蒸馏技能时遇到 **400 invalid parameter value**：

### 排查路径
1. 检查WB日志：`/mnt/c/Users/18502/.workbuddy/logs/YYYY-MM-DD/`
2. 检查最近task：`/mnt/c/Users/18502/.workbuddy/tasks/`
3. 查看WB版本：`session/*.json` 中 `"version": "2.94.2"` 等

### 常见原因
- 人物名称包含WB API不接受的字符或格式
- 缺失必填参数（skill name、path等）
- WB中间件版本与skill不兼容

### 回退方案：Hermes直接蒸馏
当WB报错时，直接在Hermes中复刻蒸馏流程：
1. 使用 `delegate_task` 启动6个并行调研agent
2. 直接在 `~/.hermes/skills/` 下创建skill目录
3. 撰写 `SKILL.md` 并运行质量自检
4. 完成后将最终skill文件同步到WB技能目录

---

## 信息源优先级

| 来源 | 揭示什么 | 权重 |
|------|---------|------|
| 用户提供的一手素材 | 完整原文 | 最高+ |
| 本人著作 | 系统性思考 | 最高 |
| 长对话/访谈 | 即兴思维过程 | 最高 |
| 实际决策记录 | 真实行为 vs 声称 | 最高 |
| 社交媒体 | 表达风格、即时反应 | 中等 |
| 他人评价 | 外部视角、盲点 | 中等 |
| 二手转述 | 参考但需验证 | 低 |

---

## 触发词速查

| 用户说 | 路径 |
|--------|------|
| 「蒸馏XX」「造skill」 | 直接蒸馏 |
| 「XX的思维方式」 | 直接蒸馏 |
| 「做个XX视角」 | 直接蒸馏 |
| 「我想提升XX」 | 诊断推荐 |
| 「有没有一种思维方式能帮我...」 | 诊断推荐 |
| 「我需要一个思维顾问」 | 诊断推荐 |
