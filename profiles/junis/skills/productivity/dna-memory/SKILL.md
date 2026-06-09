---
name: dna-memory
display_name: DNA Memory 韬忆
description: DNA记忆系统——三层记忆架构（工作→短期→长期）+ 权重衰减 + 反思循环 + 模式归纳 + 记忆图谱 + 质量评估 + 自我强化 + 对抗验证 + 蒸馏压缩 + 信号提取。吸收自DNA Memory v3.0（AI酋长Andy），融合Hermes原生工具。让Agent不只是记住，而是真正学会。
category: productivity
trigger_keywords: [记忆, 记住, 反思, 回顾, memory, recall, 学习, 忘记, 遗忘, 归纳, 模式, 沉淀, 关联, 图谱, 蒸馏, 压缩, 强化, 验证, 信号]
related_skills: [memory, session_search, skill_manage, three-strikes-promotion]
---

# DNA Memory — DNA 记忆系统 v4.0

> 吸收自 AI酋长Andy 的 DNA Memory v3.0（AIPMAndy/dna-memory）
> 融合 Hermes 原生工具链 + 韬定律 + 三振晋升规则
>
> **核心理念：人脑不是硬盘。** 重要的反复强化，不重要的主动遗忘，零散的归纳为模式。
>
> 语：让 Agent 不只是记住，而是真正学会。

---

## 三层记忆架构

```
┌──────────────────────────────────────────────────┐
│  工作记忆 (Working Memory)                        │
│  ├── 当前会话的临时信息                            │
│  ├── 容量：7条，超出则淘汰最不重要的                │
│  └── 会话结束时筛选值得保留的 → 推入短期             │
└──────────────────────────────────────────────────┘
                         ↓ 筛选
┌──────────────────────────────────────────────────┐
│  短期记忆 (Short-term Memory)                     │
│  ├── 近期（7天）的重要信息，上限100条               │
│  ├── 带衰减权重，不访问会逐渐遗忘                   │
│  ├── Hermes 的 memory 工具 = 此层                  │
│  └── 达容量上限或反思触发 → 巩固为长期               │
└──────────────────────────────────────────────────┘
                         ↓ 巩固/归纳
┌──────────────────────────────────────────────────┐
│  长期记忆 (Long-term Memory)                      │
│  ├── 经过验证的持久知识，上限500条                  │
│  ├── 归纳后的认知模式（Pattern）                   │
│  ├── Hermes skill / Obsidian笔记 = 此层            │
│  └── 低频访问自动压缩到冷存储                       │
└──────────────────────────────────────────────────┘
```

---

## 与韬定律的关系

| DNA Memory 机制 | 韬定律映射 |
|:---------------|:-----------|
| 权重衰减+遗忘 | **做对的事 > 做更多的事** — 知识太多=知识太少，自动清理噪音 |
| 模式归纳（Pattern）| **改连接>加节点** — 零散记忆归纳为模式=建立结构 |
| 反思循环 Reflect | **修三次不好→换维** — 重复出现的问题进反思，否则遗忘 |
| 记忆蒸馏 | **改连接>加节点** — 合并相似记忆，减少冗余连接 |
| 记忆图谱 | **改连接>加节点** — 建立关联本身就是优化连接 |
| 进化策略切换 | **换维度破局** — 记忆管理策略也可换维 |

---

## 记忆类型

所有写入记忆的内容，先判断属于哪种类型：

| 类型 | 说明 | 示例 | 权重基线 |
|:----|:-----|:-----|:--------:|
| `fact` | 事实信息 | "用户的微信是 XXX" | 0.5 |
| `preference` | 用户偏好 | "喜欢简洁直接的回复" | 0.7 |
| `skill` | 学到的技能 | "飞书 API 限流时要分段请求" | 0.6 |
| `error` | 犯过的错误 | "不要用 rm，用 trash" | 0.8 |
| `pattern` | 归纳的模式 | "推送 GitHub 前先检查网络" | 0.7 |
| `insight` | 深层洞察 | "用户更看重效率而非完美" | 0.6 |
| `decision` | 做出的决策 | "采用方案A而非方案B，因为..." | 0.6 |

**判断优先级：** correction > error > preference > pattern > insight > skill > decision > fact

---

## 记忆生命周期管理

### 1. Signal Extraction — 信号提取（新增 v4.0）

从对话中自动提取"值得记住的信号"，基于信号模式匹配：

| 信号类型 | 触发模式 | 置信度 | 映射记忆类型 |
|:---------|:---------|:------:|:------------|
| `correction` | "不是…而是"、"错了…正确的是"、"改成" | 0.8-0.95 | error + skill（各一条）|
| `preference` | "我喜欢"、"以后"、"默认"、"必须"、"记住" | 0.8-0.95 | preference |
| `decision` | "决定…"、"选择…而不是"、"采用…" | 0.8-0.9 | decision |
| `error` | "失败原因"、"踩坑"、"报错"、"bug" | 0.8-0.9 | error |
| `workflow` | "先…再"、"流程…"、"步骤…" | 0.8-0.85 | skill |
| `skill` | "学到…"、"方法是…"、"解决方案" | 0.8-0.9 | skill |

**用法：** 当用户纠正、给出偏好、分享经验时，自动提取信号→判断是否值得记→写入对应类型。

### 2. 记录 → 判断该不该记

不是什么都记。记录前自问：
- 这是 fact / preference / skill / error / pattern / insight / decision 中的哪一种？
- 如果一年后回头看，这条还有意义吗？
- 如果是临时信息（当前任务的执行细节）→ 不记
- 置信度低于 0.6 的信号 → 暂不记，继续观察

### 3. 强化权重

| 事件 | 权重变化 |
|:----|:---------|
| 被访问/使用 | +0.1 |
| 被用户确认正确 | +0.2 |
| 被用户纠正 | 标记为错误，创建新记忆 |
| 关联到其他记忆 | +0.05 |
| 被归纳为模式 | 升级为 skill 或知识库笔记 |
| 7天未访问 | -0.1 |
| 被用户明确说"不对" | -0.3，若<阈值则进入待清理 |

### 4. 衰减与遗忘

- **热度衰减：** 7天没被调用的 memory → 权重 -0.1/周
- **阈值遗忘：** 权重低于 0.25 的 → 从活跃记忆降级
- **重要保护：** 用户说"记住这个"的 → 永久不衰减
- **遗忘不是删除：** 降级的记忆进入"冷存储"（memory/archive/），可恢复

### 5. 反思循环（Reflect Loop）

**触发时机：**

| 时机 | 具体动作 |
|:----|:---------|
| 复杂任务完成后（≥5次 tool call） | 轻量反思 → 判断是否为 skill/pattern/insight |
| 用户纠正我后 | 立即记 error + 正确做法各一条，关联两者 |
| 同一模式出现≥3次 | 触发三振晋升 → 评估是否需要升级 |
| 用户说"记住这个""刚才学到了什么" | 走完整反思流程 |
| 会话自然结束前 | 快速扫描有没有值得一提的模式/偏好/错误 |

**反思流程：**

```
回顾近期记忆（session_search）
  → 识别重复出现的信息/模式
  → 判断是否可归纳为 pattern
  → 如果是 → 写入文件（.md 笔记或 skill 文件）
  → 如果不是 → 保留在 memory 继续观察
  → 检查是否有矛盾记忆 → 触发对抗验证
```

**关键规则：** 反思的结果必须落地为文件（pattern/insight/skill → skill或笔记；preference → memory；error → 同时记错误+正确两条）。

---

## 高级能力（原版 v3.0 精华）

### 🕸️ 记忆图谱（Memory Graph）

每条记忆可与其它记忆建立关联关系，形成知识网络：

| 关系类型 | 含义 | 示例 |
|:---------|:-----|:-----|
| `related` | 相关 | 两个关于 API 的记忆 |
| `causes` | 导致 | "超时"导致"重试" |
| `contradicts` | 矛盾 | "偏好A"与"偏好B"冲突 |
| `extends` | 扩展 | 一个技能扩展另一个 |
| `supersedes` | 替代 | 新方案替代旧方案 |
| `solution` | 解决方案 | error → skill 的因果关系 |

**自动关联：** 当两条记忆内容相似度 > 0.7 时自动建立 related 关系。
**矛盾检测：** contradict 关系触发对抗验证流程（见下）。

**使用场景：**
- error 记忆关联到对应的 skill 记忆（"错误→解决方案"链）
- 一条决策关联其影响的所有后续 memory
- 模式归纳时将原始记忆关联到新 pattern

### 📊 记忆质量评估（Memory Quality）

每条记忆自动评分，高质保留，低质清理：

| 维度 | 权重 | 说明 |
|:----|:---:|:-----|
| 访问频率 `access_frequency` | 25% | 被调用的次数/周期 |
| 新鲜度 `freshness` | 15% | 最近更新的时间 |
| 具体性 `specificity` | 20% | 内容是否具体可执行 |
| 验证状态 `validation` | 20% | 是否被用户确认过 |
| 关联度 `connections` | 10% | 关联到多少条其他记忆 |
| 重要性 `importance` | 10% | 当前权重值 |

**综合质量分 = Σ(维度分 × 权重)**

| 质量等级 | 分范围 | 处理 |
|:---------|:------:|:-----|
| 🟢 优 | ≥ 0.7 | 长期保留，优先调用 |
| 🟡 中 | 0.4-0.7 | 继续观察 |
| 🔴 低 | < 0.4 | 考虑清理或压缩到冷存储 |

### 🗜️ 记忆压缩（Memory Compression）

低频访问但仍有价值的记忆 → 压缩到冷存储：

```python
def compress(threshold_weight=0.3, days_unused=30):
    """将权重低且长期未访问的记忆归档到冷存储"""
    candidates = select where weight < threshold_weight
                 AND last_accessed < now - days_unused
                 AND type NOT IN ('preference', 'pattern')
    for m in candidates:
        archive_to_compressed(m)  # memory/archive/compressed_{date}.json
        mark_compressed(m)
```

冷存储中的记忆不计入活跃容量，可按关键词搜索恢复。

### 🔄 自我强化（Self-Reinforcement）

记忆不只是存，还要验证它是否仍然正确：

```
定期扫描高权重记忆
  → 检查是否有与之矛盾的记忆（矛盾检测）
  → 如果长期未被验证，降低置信度
  → 如果被多次调用且无矛盾，提升权重（验证强化）
  → 用户确认正确的记忆永久标记 Verified
```

| 事件 | 效果 |
|:----|:-----|
| 记忆被正确使用5次以上 | 标记为 Verified |
| 记忆被找到矛盾 | 降低权重，标记待解决 |
| 记忆30天未被调用也未验证 | 降低权重+置信度 |

### ⚡ 对抗验证（Adversarial Validation）

主动寻找记忆之间的矛盾，防止系统积累错误知识：

```python
# 矛盾检测规则
CONTRADICTION_RULES = [
    ("preference", "preference"),   # 偏好之间有矛盾
    ("skill", "skill"),             # 技能之间矛盾
    ("error", "skill")              # 错误说的和技能说的矛盾
]

# 检测到矛盾后的处理
1. 标记两条记忆为含矛盾
2. 降低两条的置信度
3. 创建一条新记录描述该矛盾
4. 等待用户裁决（下次调用时询问）
```

### 🧪 记忆蒸馏（Memory Distillation）

多条同级相似记忆 → 合并为一条高质量记忆：

```python
def distill():
    """合并相似记忆"""
    similar_groups = find_similar_groups(threshold=0.85)
    for group in similar_groups:
        merged = {
            'content': merge_texts([m.content for m in group]),
            'weight': max(m.weight for m in group),
            'sources': [m.id for m in group],
            'type': group[0].type,
            'verified': all(m.verified for m in group)
        }
        write_merged(merged)
        soft_delete(group)  # 标记已合并
```

### 🔍 元记忆追踪（Meta Memory）

追踪记忆系统本身的演化，回答"我的记忆系统健康吗"：

| 指标 | 说明 |
|:-----|:-----|
| 总记忆数 | 各层记忆的数量 |
| 增长率 | 每周新增/清理比例 |
| 质量分布 | 优/中/低比例 |
| 矛盾率 | 含矛盾的记忆占比 |
| 蒸馏率 | 已合并的记忆占比 |
| 健康度 | 综合得分 |

**使用场景：** 每周回顾时看一眼，判断是否需要切换进化策略。

### 🧠 会话记忆（Session Memory）

每个会话的独立上下文容器，会话结束后自动汇总：

```
会话开始 → 创建会话容器
  → 记录关键对话内容（working memory）
  → 记录做出的决策和原因
  → 记录遇到的错误和解决方案
会话结束 → 筛选值得长期保留的 → 推入短期记忆
  → 丢弃纯临时的执行细节
  → 生成会话摘要
```

### 💭 思维记忆（Thought Memory）

不只是存"用户说了什么"，更存"我从中学到了什么"：

```python
thought = {
    'trigger': '用户纠正了xxx',
    'observation': '发现的模式或问题',
    'insight': '提炼出的认知',
    'implication': '对未来行为的改变',
    'confidence': 0.8
}
```

思考型记忆直接进入短期记忆，不经过工作记忆，因为它已经过加工。

### 🎯 进化策略（Evolution Strategy）

四种策略模式，根据不同阶段切换：

| 策略 | 新记忆权重 | 强化权重 | 衰减权重 | 置信度阈值 | 适用场景 |
|:----|:---------:|:--------:|:--------:|:----------:|:---------|
| **balanced** 平衡模式 | 0.5 | 0.3 | 0.2 | 0.7 | **默认，日常运行** |
| **aggressive** 激进模式 | 0.8 | 0.15 | 0.05 | 0.6 | 新用户、新项目，需要快速学习 |
| **conservative** 保守模式 | 0.2 | 0.4 | 0.4 | 0.85 | 系统稳定后，聚焦质量 |
| **cleanup** 清理模式 | 0.0 | 0.2 | 0.8 | 0.95 | 定期整理日，只保留最优质的记忆 |

**切换触发：** 元记忆追踪发现健康度下降 → 切换到 cleanup；新领域学习 → 切换到 aggressive；日常 → 保持 balanced。

---

## 自动触发点

| 时机 | 动作 |
|:----|:-----|
| **新会话开始** | 检查是否有到期要衰减的记忆 → 调权 |
| **用户纠正我** | 创建 error + skill 各一条，用 causes 关联 |
| **同一件事出现≥3次** | 触发三振晋升 → 评估是否归纳为 pattern |
| **用户说"记住这个"** | 写入最高权重 preference，标记不可衰减 |
| **完成复杂任务后** | 轻量反思：学到了什么 |
| **信号匹配命中** | 自动提取信号，按类型写入 |
| **记忆互相关联≥3条** | 尝试归纳为 pattern |
| **检测到矛盾记忆** | 触发对抗验证 |
| **活跃记忆≥80%容量** | 触发蒸馏 + 压缩 |
| **每周回顾** | 查看元记忆健康度，评估策略是否合适 |

---

## Python 脚本（增强工具）

原版 DNA Memory v3.0 的 30+ Python 脚本已部署到 Hermes，使用 SQLite 实现全功能记忆管理：

**存储路径：** `~/.hermes/resources/dna-memory/`
**入口脚本：** `evolve.py`

| 命令 | 功能 |
|:----|:-----|
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py remember "内容" -t preference -i 0.8` | 记录记忆 |
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py recall "关键词"` | 搜索记忆（按相关度排序）|
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py reflect` | 触发反思循环 |
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py decay` | 执行遗忘机制 |
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py link <id1> <id2> -r causes` | 建立记忆关联 |
| `python3 ~/.hermes/resources/dna-memory/scripts/evolve.py stats` | 查看统计 |
| `python3 ~/.hermes/resources/dna-memory/scripts/memory_graph.py graph` | 查看关联图谱 |
| `python3 ~/.hermes/resources/dna-memory/scripts/memory_quality.py` | 执行质量评分 |
| `python3 ~/.hermes/resources/dna-memory/scripts/memory_reinforcement.py` | 执行自我强化循环 |
| `python3 ~/.hermes/resources/dna-memory/scripts/memory_distillation.py` | 执行蒸馏合并 |
| `python3 ~/.hermes/resources/dna-memory/scripts/memory_compression.py` | 执行压缩归档 |
| `python3 ~/.hermes/resources/dna-memory/scripts/meta_memory.py` | 查看元记忆报告 |
| `python3 ~/.hermes/resources/dna-memory/scripts/adversarial_validation.py` | 执行矛盾检测 |
| `python3 ~/.hermes/resources/dna-memory/scripts/session_memory.py save` | 保存当前会话记忆 |
| `python3 ~/.hermes/resources/dna-memory/scripts/thought_memory.py` | 写入思维记忆 |
| `python3 ~/.hermes/resources/dna-memory/scripts/signal_extractor.py extract "输入文本"` | 从文本提取记忆信号 |
| `python3 ~/.hermes/resources/dna-memory/scripts/dna_memory_daemon.py start` | 启动后台守护（自动 reflect + decay）|

**使用原则：**
- 日常使用优先走 Hermes 原生工具（memory、session_search、skill_manage）
- SQLite 脚本用于批量操作、质量审查、系统维护
- 脚本执行结果可与 memory 工具双向同步

---

## 执行约束

- 不要在会话中频繁调用 memory — 每条写入/读取都有 token 成本
- 优先用 `session_search` 回顾旧会话内容（更便宜）
- `memory` 只存「跨会话仍需要」的持久信息
- 一条记忆的规格：简短的1-2句话 + 类型标签
- 信号提取不是 OCR 式的每句扫描，而是在关键节点（用户纠正/明确表态/经验分享后）触发
- 反思不必每次会话都做，"有东西可反思"时才做

---

## 与其他技能/工具的关系

| 技能/工具 | 分工 |
|:----------|:-----|
| **memory 工具** | 短期记忆层，存跨会话持久信息 |
| **session_search** | 工作记忆回顾，搜索旧会话内容 |
| **skill_manage** | 长期记忆升级 — 模式/技能升格为 skill |
| **三振晋升规则** | 反思循环触发器 — 重复≥3次触发晋升 |
| **deep-research** | 独立方法论，不混入记忆管理 |
| **SQLite evolve.py** | 批量记忆操作、质量审查、系统维护 |
| **Obsidian vault** | 长期记忆中的知识库层 |

---

## ⚠️ Pitfalls

- ❌ 不要什么事都记 — 执行步骤、临时路径、当前任务状态 → 不记
- ❌ 不要在 memory 里存结构化长文 — 这是知识库笔记的事
- ❌ 不要同时用 Hermes memory + SQLite 脚本写同一份数据 — 选一个工具
- ✅ preference 和 pattern 优先于 fact — 用户偏好比零散事实更有价值
- ✅ 被纠正时同时记 error + skill — 记住错的和对的各一条，用 causes 关联
- ✅ 反思不是开新会话，是在当前会话的自然间隔做一次轻量 review
- ✅ 记忆图谱不是必须的，只在有明显关联时才建立 — 过度关联等于没有关联
- ✅ 进化策略不是日常操作，只在元记忆报告提示时才考虑切换

---

## 参考

> DNA Memory v3.0 原文路径：`/mnt/d/龙虾技能/skill/dna-memoryv3.0-main/dna-memory-main/`
> 作者：AI酋长Andy（AIPMAndy/dna-memory）
> 脚本路径：`~/.hermes/resources/dna-memory/scripts/`
> 存储路径：`~/.hermes/resources/dna-memory/memory/`
