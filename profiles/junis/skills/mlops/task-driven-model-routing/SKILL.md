---
name: task-driven-model-routing
description: 任务驱动的模型路由策略。不要所有任务用一个默认模型，而是根据任务特征（五信号判断法）自动路由到最合适的模型。核心框架可适用于Hermes/WorkBuddy/Claude Code等多模型智能体系统。
trigger_keywords:
  - 模型选择
  - 模型路由
  - 选模型
  - 模型池
  - 任务路由
  - 模型调度
  - multi-model routing
  - model selection strategy
  - 五信号
---

# 任务驱动模型路由 (Task-Driven Model Routing)

> 核心原则：不要选最强，要选最合适。不同任务用不同模型。

## 五信号判断法

接到任务后，先提取以下5个特征信号：

```
① 输入类型   → 文本 / 截图 / 视频 / 代码 / 文档 / 混合
② 任务深度   → 单步回答 / 多步骤执行 / 长链推理(5+步)
③ 上下文长度 → 短(<10K) / 中(10K~50K) / 长(50K~128K) / 极长(>128K)
④ 交付形态   → 回答 / 代码 / PPT / Word报告 / 表格 / 方案
⑤ 成本敏感度 → 高价值单次 / 中等 / 低成本批量
```

## 四类模型池

| 池子 | 分数区间 | 用途 | 选择优先级 |
|:----|:-------:|:-----|:---------|
| 🏛️ **主力池** | 90~100 | 高价值任务 | 稳定性优先 |
| 🎯 **专项池** | 85~89 | 特定能力（视觉/工具链） | 匹配度优先 |
| ⚖️ **性价比池** | 80~84 | 日常/批量/长文档 | 单位成本优先 |
| 🔬 **探索池** | 75~79 | 试点/成本敏感 | 成本优先 |

## 路由三原则

### 1. 高价值 → 优先稳定性
- 任务影响大、失败成本高、需要连续执行
- ✅ 选主力池模型
- ✅ 必要时用第二个模型复核

### 2. 专项任务 → 优先匹配度
- 出现截图/视频/设计稿 → 切视觉模型
- 出现 MCP 工具链 → 切工具调用模型
- 长链执行 → 切智能体能力更稳定的模型
- ⚠️ 不要只看综合分

### 3. 批量任务 → 优先单位成本
- 摘要/分类/抽取/长文档预处理/高并发
- ✅ 先用高性价比模型做第一轮
- ✅ 关键结果交给强模型复核

## 路由决策树

```
任务进来
  │
  ├─ 有截图/视频/设计稿？ → 🎯 视觉优先
  ├─ 需要多工具多步骤？ → 🎯 工具链优先
  ├─ 文件>50页或批量处理？ → ⚖️ 性价比优先
  ├─ 交付物是PPT/Word/方案？ → 🏛️ 主力优先
  ├─ 代码工程或复杂推理？ → 🏛️ 主力优先
  ├─ 合规/私有化验证？ → 🔬 探索优先
  └─ 简单问答/日常？ → ⚖️ 性价比优先
```

## Python 路由引擎实现要点

详细实现参考：`references/python-router-implementation.md`
当前模型池表（2026-05 TokenHub）：`references/model-pool-tables.md`

```python
class ModelRouter:
    """核心结构"""
    
    def classify_scene(self, task: str) -> tuple:
        """识别任务场景（基于关键词匹配）"""
        ...
    
    def resolve_model(self, scene, primary, secondary, fallback) -> str:
        """按优先级返回第一个可用模型"""
        ...
    
    def route(self, task: str) -> RouteResult:
        """主路由方法"""
        scene, matches, score = self.classify_scene(task)
        ...
```

详细实现参考：`references/python-router-implementation.md`

## 注意事项

### 模型池维护
- 模型排名随时间变化，表格需要季度更新
- 新模型上线后需测试其在不同场景下的表现
- 保持最少2个备选模型以防主模型故障

### 分类器设计
- 关键词匹配适合快速原型，但可能有歧义
- 长文本任务描述比短描述的匹配更准确
- 无法识别场景时走通用路由（根据任务特征判断）

### 与下游系统集成
- 返回的 model_id 需要与下游系统的模型注册表一致
- WB models.json 的 id 字段需要与路由引擎的 model_id 匹配
- Hermes 使用 `/model` 命令切换模型，路由结果需要转换为 Hermes 的 model 名称

## 跨Provider路由：免费 vs 付费

> 适用场景：当你有多个模型通道（如 NVIDIA NIM 免费、DeepSeek官方付费）时，在 bot/profile 级别做成本最优分配。

### 核心洞察

**NVIDIA NIM（integrate.api.nvidia.com/v1）免费通道包含的关键模型（经实测）：**

| 模型 | NIM 免费 | DeepSeek 官方付费 | 差异 |
|------|----------|-----------------|------|
| `deepseek-ai/deepseek-v4-flash` | ✅ **免费** | 💰 按量计费 | 同模型，无差异 |
| `deepseek-ai/deepseek-v4-pro` | ✅ **免费** | 💰 按量计费 | 同模型，无差异 |
| `stepfun-ai/step-3.7-flash` | ✅ **免费** | 💰 按量计费 | 同模型，无差异 |

⬆ **这意味着：日常高频使用的 DeepSeek 模型可以在 NIM 上免费运行。**

### 多Bot路由架构

当你有多个角色Bot时，路由策略分两层：

```
                    ┌───────────────────┐
                    │   任务进入          │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │  按Bot身份分流      │
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          BotA          BotB          BotC
       ┌─────┴─────┐  ┌──┴──┐  ┌─────┴─────┐
       │ NIM 免费   │  │ NIM │  │ NIM        │
       │ (default)  │  │ 免费│  │ 免费       │
       └─────┬─────┘  └──┬──┘  └─────┬─────┘
             │           │           │
             └───────────┼───────────┘
                         │ 失败时
                         ▼
                  ┌──────────────┐
                  │ 付费兜底      │
                  │ (DeepSeek官方) │
                  └──────────────┘
```

### 分配原则

| 任务类型 | 默认通道 | 原因 |
|---------|---------|------|
| 高频执行/调度（cron/terminal/github） | NIM 免费 | 量最大，免费是必须的 |
| 深度思辨/哲学 | NIM 免费（v4-pro） | 偶尔调用，NIM质量足够 |
| 分析框架/竞品洞察 | NIM 免费 | 中等频率，免费划算 |
| 日常对话 | NIM 免费（v4-flash） | 高频，免费 |
| NIM 宕机/限速时 | DeepSeek 官方（付费） | 兜底，正常情况不触发 |

### Hermes 配置实现（实际已验证的配置）

在每个 profile 的 config.yaml 中，使用 `provider: custom` 模式指向 NVIDIA NIM：

```yaml
# 默认走 NIM 免费通道
model:
  default: deepseek-ai/deepseek-v4-flash
  provider: custom
  base_url: https://integrate.api.nvidia.com/v1
  api_key_env: OPENAI_API_KEY

# 定义 DeepSeek 官方付费通道作为兜底
providers:
  deepseek:
    api_key_env: DEEPSEEK_API_KEY
    base_url: https://api.deepseek.com
    models:
    - deepseek-v4-flash
    - deepseek-v4-pro

# 失败时自动 fallback 到 DeepSeek 官方付费
fallback_providers:
- provider: deepseek
  models:
  - deepseek-v4-flash
  activation:
    mode: sequential
    min_priority: 1
```

> ⚠️ **配置陷阱（实测发现）：** 
> - Hermes 不支持 `custom_providers` 命名块，也不支持 `custom:nvidia` 后缀写法。NVIDIA NIM 必须用 `provider: custom` 配合内联 `base_url` + `api_key_env`。
> - `fallback_providers` 中的 provider 名必须匹配 `providers:` 块中定义的 key。
> - **patch 工具可能虚假成功：** 改 config.yaml 后必须 `head -5` 或 `grep` 确认内容实际写入磁盘（junis/saodiseng 各出现一次 patch 报告 success 但文件未修改）。

### 双模式手动切换

除了自动 fallback，还可以手动在模式间切换：

| 命令 | 效果 |
|------|------|
| `/speed` | 切到DeepSeek官方（快稳，花钱） |
| `/free` | 切回NIM（免费，可能慢） |

实现方式：`/speed` 使用 `/model deepseek deepseek-v4-flash`；`/free` 使用 `/model custom deepseek-ai/deepseek-v4-flash`。

### 成本效益

- 日常 95%+ 调用走 NIM 免费 → 成本趋近于 0
- 仅 NIM 不可用时走付费兜底 → 极小概率
- 手动可通过 `/model nvidia` / `/model deepseek` 一键切换

### 注意事项

- 需要为每个 Bot profile 单独配置 provider 和 fallback（profile 级配置不继承主 config）
- NIM 免费通道可能有调用频率限制或延迟，不可用于延迟敏感场景（如实时对话可考虑保留付费通道）
- NIM 模型 ID 采用 `组织名/模型名` 格式（如 `deepseek-ai/deepseek-v4-flash`），区别于 DeepSeek 官方的简写格式
- **模型名不对称问题：** NIM上的 `deepseek-ai/deepseek-v4-flash` 和 DeepSeek官方的 `deepseek-v4-flash` 是同一个模型但不同名字。fallback时Hermes会按models列表中的名字请求，所以两边的模型名必须对得上
- **自动通知：** NIM不可用触发fallback时，应通知用户一次（仅首次），后续同会话不再重复
- **自动恢复：** 每条请求独立探测，NIM恢复后下一条自动切回，无需手动操作
- 建议定期用 `curl` 刷新 NIM 模型列表，确认免费模型未变动

详细 NIM 模型目录见 `references/nvidia-nim-catalog.md`。
