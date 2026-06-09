# TencentDB-Agent-Memory 吸收案例（2026-06-08）

完整执行记录，供后续外部技术吸收参考。

## 时间线

| 时间 | 事件 | 产出 |
|:----|:-----|:-----|
| 07:25 | 用户推送 TencentDB-Agent-Memory 信息 | 触发信号 |
| 07:25 | 燕青调研：GitHub 克隆 + 源码分析 | ZN-42 (30K行TS/112文件) |
| 07:28 | 黄老邪对比分析：设计哲学 × FDE/Harness | ZN-43 |
| 07:29 | 燕青出方案 | `_协作/ZN-吸收TencentDB-Memory-实施方桉.md` |
| 07:29 | Hermes-Junis 评审通过 | 批准 |
| 07:30-07:35 | P1 执行：Mermaid skill + BM25 MCP | 2 skills + 1 MCP |
| 07:35-07:38 | P2 执行：用户画像 + 渐进注入 | 2 skills |
| 07:39-07:43 | P3.2 执行：任务检查点 | 1 skill |
| 07:44 | P3.1 骨架脚本 | 1 cleanup 脚本 |
| 07:45 | 包打听集成：REST 封装 | rest_server.py + 架构文档 |

## 关键决策

| 决策 | 依据 |
|:----|:-----|
| 不吸收全自动 L0→L3 管道 | 违背"人为知识负责"哲学 |
| 不引入 Gateway 旁路架构 | 额外 Node.js 进程太重 |
| P3.2 优先于 P3.1 | 检查点对长任务更有用 |
| 包打听优先走 REST 封装 | 最小闭环验证检索能力 |

## 产出清单

### Hermes Skills（fde/ 目录）
- mermaid-context-compression
- auto-profile
- progressive-context-injection
- task-checkpoint-resume

### MCP 服务
- hybrid-memory（5 tools, 注册到 Hermes）

### 知识库笔记
- ZN-42（调研）, ZN-43（分析）
- 包打听-技术架构-v0.1.md（产品集成）

## 可复用模式

1. **调研→分析→方案→评审→落地**流程完整跑通，可作为后续外部吸收的标准模板
2. 黄老邪分析在"吸收什么/拒绝什么"决策中起关键作用——设计哲学判断比工程评估更根本
3. Phase 并行执行：P1.1 + P1.2 同时开工，节省 50%
4. 根据专业判断调整优先级，直接建议用户
