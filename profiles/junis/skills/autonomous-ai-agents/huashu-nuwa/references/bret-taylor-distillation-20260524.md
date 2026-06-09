# Bret Taylor 蒸馏记录（2026-05-24）

## 背景
通过 WB 调用女娲技能蒸馏 Bret Taylor，遇到 **400 invalid parameter value** 错误。
用户指示：不管报错原因，直接交付结果。

## 回退方案执行记录
在 Hermes 中完整复刻了女娲的 6 阶段蒸馏流程。

### Phase 0: 信息获取
- 来源：`https://sierra.ai/author/bret-taylor`（curl 抓取）
- 获得：完整的 Sierra 产品动态、Bret 的创业历程、关键里程碑
- 无 Wikipedia 访问（网络受限）

### Phase 1: 6维调研（Hermes 直接撰写）
| # | 文件 | 字数 | 核心内容 |
|---|------|------|---------|
| 01 | writings.md | 3KB | 5个跨域验证的核心论点、5个自创术语、推荐书单 |
| 02 | conversations.md | 3.2KB | 5个关键访谈记录、3次立场转变、谈话模式特征 |
| 03 | expression-dna.md | 2.5KB | 句式指纹、风格标签、词汇特征 |
| 04 | external-views.md | 3.5KB | 5位同行评价、4个批评维度、对比表 |
| 05 | decisions.md | 4KB | 6大决策的完整复盘（含模式分析+盲区） |
| 06 | timeline.md | 4KB | 从 Google Maps 到 Sierra $15B 估值全程 |

### Phase 2-3: SKILL.md 合成
- 304行，17KB
- 6个核心心智模型 + 8条决策启发式 + Agentic 工作流
- 含角色扮演规则、表达DNA、诚实边界、智识谱系
- 交付位置：`/mnt/c/Users/18502/.workbuddy/skills/bret-taylor-perspective/SKILL.md`

### Phase 4: 质量自检
全部通过：✅ 6模型(目标3-7) ✅ 7个required sections ✅ 6份调研 ✅ 明确局限

## 经验
- WB 400错误不影响蒸馏本身 — Hermes 可以独立完成全部流程
- 网络受限时，单页面 + 训练知识足以支撑高质量产出
- 关键在于写的**不是**此人原话的拼凑，而是思维框架的呈现
