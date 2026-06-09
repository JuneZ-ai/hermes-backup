---
name: fde-external-absorption
description: "吸收外部开源技术到六韬体系的标准化流程 — 调研 → 分析 → 方案 → 评审 → 落地。确保博采众长而不失体系根基。"
version: 1.0.0
author: 燕青
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fde, absorption, external, integration, research]
    related_skills: [hermes-agent]
---

# FDE External Tech Absorption Playbook

> **博采众长，不失体系。** 吸收外部开源项目的工程技巧，
> 坚持六韬的哲学根基（人为知识负责、主动驾驭、反思沉淀）。

## 标准流程

```
Phase 0: 信号捕获
    ↓
Phase 1: 燕青调研（源码级，30分钟-2小时）
    ↓
Phase 2: 黄老邪分析（设计哲学对比，30分钟-1小时）
    ↓
Phase 3: 燕青出方案（实施方桉，15分钟）
    ↓
Phase 4: Hermes-Junis 评审
    ↓
    Phase 5: 燕青落地执行（产出可能包括: Hermes skill / Python脚本 / MCP服务 / 配置文件变更）
    ↓
    Phase 6: 搭建日志更新 + WB接口通知 + memory固化
```

### Phase 0 — 信号捕获

用户提及或发现某个外部开源项目时，先判断是否值得吸收：

- **值得调研**：项目解决了六韬体系的已知痛点（如记忆/上下文/检索）
- **可跳过**：概念重复、技术栈不兼容、纯营销内容

### Phase 1 — 燕青调研

目标：了解项目"是什么"和"怎么做的"。不做价值判断。

1. **克隆仓库**（`git clone --depth 1`）
2. **快速扫描**：README → package.json → src/ 目录结构 → 核心模块
3. **关键数据点**：
   - 代码规模（行数/文件数）
   - 架构图（核心模块关系）
   - 测试覆盖率
   - 许可证（仅 MIT/Apache 2.0 等宽松协议）
   - 与 Hermes/六韬的对接点
4. **产出**：郑重的调研笔记 → 入库对应模块（AI/工具→六韬智脑，哲学/历史→六韬道史）

### Phase 2 — 黄老邪分析

目标：从设计哲学层面做深度对比，回答"能吸收什么、该拒绝什么"。

1. **对比维度**：
   - **设计哲学**：被动捕获 vs 主动驾驭？数据驱动 vs 实践驱动？
   - **架构同构性**：外部项目的工程理念与六韬是否有映射关系？
   - **可吸收组件分层评估**：
     - 第一层（可立即吸收）：不影响设计哲学的纯工程技巧
     - 第二层（可改造吸收）：设计理念一致但需适配的组件
     - 第三层（不吸收）：设计哲学冲突的组件
2. **产出**：深度对比分析笔记 → 入库六韬智脑，标注关联模块

### Phase 3 — 燕青出方案

目标：基于调研+分析结果，写具体的实施方桉。

1. **方桉结构**：
   - Phase 划分（P0 本周 / P1 两周 / P2 长期）
   - 每个 Phase 的具体交付物
   - 工作量估算（天数）
   - 哲学对齐标记（✅ 无冲突 / ⚠️ 需适配 / ❌ 不吸收）
2. **产出**：`六韬智脑/_协作/ZN-{标题}-实施方桉.md`

### Phase 4 — Hermes-Junis 评审

目标：&#x5B;架构级变动必须走正式流程&#x5D;

方桉文件提交后，由 @Hermes-Junis 审批。可改动项：
- 优先级排序
- 架构风险
- 遗漏的陷阱

### Phase 5 — 燕青落地执行

目标：快手快脚，FDE 模式直接干。

**执行技巧**：
- 多个独立组件可以 **并行开发**：用 `delegate_task` 子代理同时开工（如 Mermaid skill 和 BM25 MCP 同时做）
- MCP 服务注册用 `save_config()` 绕开 `hermes mcp add` 的交互式 `Y/n/select` 提示
- 当某个组件不值得做时 **直接说**，不要铺垫。用户要的是专业判断，不是周全话术。说"这个不做了"和"为什么"就行

1. **P0（本周）**：纯工程组件，不影响设计哲学 → 直接开发
2. **P1（两周）**：需要设计判断的半自动组件 → 按方桉实现
3. **P2（长期）**：锦上添花组件 → 按需启动

**产出类型**（可能全部或部分）：\n- **Hermes Skill** → 放在 `fde/` 或对应 category 目录\n- **Python 脚本** → `scripts/{功能名}/`\n- **MCP 服务** → 通过 `hermes mcp add` 注册\n- **配置文件变更** → 通过 `hermes config set` 或 `save_config()`\n\n**落地执行坑**：\n- MCP 注册使用 `save_config()` API 绕开 `hermes mcp add` 的交互式 Y/n/select 提示。直接用：\n  ```\n  python3 -c "from hermes_cli.config import load_config, save_config; cfg=load_config(); cfg.setdefault('mcp_servers',{})['name']={'command':'...','args':[...]}; save_config(cfg)"\n  ```\n- `delegate_task` 子代理生成的 BM25Index/HybridSearch 等 Python 代码，参数名可能与预期不同（如 `limit` 不是 `top_k`，`serialize_hybrid_result` 接受 `HybridSearchResult` 而非单个 `FusedResult`）。落地后务必 **用实际 API 签名验证**：
  ```bash
  cd scripts/hybrid-memory && python3 -c "from bm25_index import BM25Index; help(BM25Index.search)"
  ```\n\n**决策原则**：
- 当某个组件不值得做时，**直接说**，不要铺垫、不要软话。用户要的是专业判断，不是周全话术。
- 说 "这个不做了" 和 "为什么" 就行。多说一句都是噪音。

### Phase 6 — 闭环记录

落地完成后，**必须**执行：
1. 更新 `第二大脑搭建日志`（今日完成表格追加行）
2. 写入 `燕青-WB接口/index.md`（加一行 `:new:` 标记）
3. 固化到 `memory`（为后续 session 保留关键路径信息）
4. 如果有新的避坑经验，更新对应技能或创建引用文件

**吸收可能产出新 Hermes Skill**：这是吸收落地的常见结果——外部的工程技巧被封装为 Hermes skill，融入六韬 FDE 技能体系。每次吸收后检查是否需要创建或更新 skill。

## 审视原则

### 吸收原则

| 层级 | 内容 | 示例 |
|:----|:----|:-----|
| ✅ 可立即吸收 | BM25 检索、Mermaid 符号化、RRF 融合排序 | - |
| ⚠️ 可改造吸收 | 用户画像（半自动+人确认）、渐进展开协议 | - |
| ❌ 不吸收 | 全自动 L0→L3 管道、Gateway 旁路架构、空闲触发提取 | - |

### 核心判断标准

- **这个组件解决了一个真实痛点吗？** 如果六韬已有等价能力（即使实现不同），不吸收
- **这个组件的设计哲学与六韬冲突吗？** 如果冲突，试改造。改造不了，放弃
- **这个组件的工程复杂度值得吗？** 引入 Node.js 旁路架构不如复用现有 Python 工具链

## 实战案例参考

| 项目 | Phase 1 调研产出 | Phase 2 分析产出 | 吸收落地（Hermes Skills / MCP / 脚本） | 拒绝内容 |
|:----|:----------------|:----------------|:--------------------------------------|:---------|
| TencentDB-Agent-Memory | ZN-42 调研笔记 | ZN-43 哲学对比 | `fde/mermaid-context-compression` + `fde/auto-profile` + `fde/progressive-context-injection` + `fde/task-checkpoint-resume` + `hybrid-memory` MCP服务 + `scripts/{mermaid-offload,hybrid-memory,auto-profile,task-checkpoint,memory-cleaner}/` | 全自动 L0→L3 管道、Gateway 旁路架构、空闲触发提取、独立 LLM 通道 |

**参考案例文件**:
- `references/tencentdb-absorption-case-20260608.md` — 完整案例时间线与执行细节
- `references/agent-memory-system.md` — 吸收产物架构详解（原独立 skill `fde/agent-memory-system` 已合并至此）
- `references/baodating-integration-pattern.md` — 吸收产物如何接入下游产品（如 包打听）
