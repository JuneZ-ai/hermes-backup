---
name: zoom-out
description: >
  跳出当前代码/问题段，给出系统级视角和更高层级的上下文。
  当用户在具体实现细节里越钻越深，或在审视一段不熟悉的代码时，加载本
  skill 让代理 zoom out 到整体架构、模块关系和系统层面。
  灵感来自 Matt Pocock (mattpocock/skills) 的 zoom-out skill。
  触发词：「zoom out」「退一步」「整体看」「系统视角」「大局」「架构层面」
---

# Zoom Out — 系统级视角

> **核心理念：** Agent 默认盯着眼前的一亩三分地。Zoom Out 强迫它退三步，看清全局。

## 何时使用

- 用户在审查一段不熟悉的代码 / 模块
- 卡在一个细节 bug 里出不来
- 需要理解「这个功能和整个系统什么关系」
- 做架构决策前需要全局视图

## 输出格式

```
## Zoom Out: {模块/功能名}

### 在系统中的位置
{这段代码属于哪个子系统 / 层 / 模块}

### 上下游关系
→ 上游输入：[谁调用它 / 从哪里来]
→ 下游输出：[它调用了谁 / 往哪里去]
↔ 同级协作：[与哪些兄弟模块交互]

### 核心职责
{3句话以内说清这个模块唯一该做的事}

### 关键设计决策
{如果没有 ADR，直接提炼代码里隐含的设计意图}
- [决策 1]
- [决策 2]

### 潜在的改进方向
{从架构层面看，这里是否存在认知负荷过高/耦合/职责混淆的问题？}
```

## 示例

```
## Zoom Out: payment-service

### 在系统中的位置
订单子域 → 结算限界上下文 → 支付网关适配层

### 上下游关系
→ 上游：order-service 发起 PaymentRequest
→ 下游：调用 Stripe API / 支付宝 SDK
↔ 同级：与 invoice-service 共享 PaymentStatus 枚举

### 核心职责
把业务支付请求翻译成具体网关的API调用，确保幂等和一致性。

### 关键设计决策
- 策略模式选网关（not if/else）
- PaymentIdempotencyKey = orderId + paymentMethod
- 失败重试 3 次 + 死信队列

### 潜在的改进方向
- PaymentStatus 枚举在与 invoice-service 共享 → 建议抽到 shared-kernel
- 重试策略硬编码 → 建议配置化
```
