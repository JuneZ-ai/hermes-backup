---
name: goskill-pattern
description: GoSkill 目标驱动执行模式——设定目标+成功标准→delegate_task子代理持续工作→验证→不达标再跑。融合自Andy的GoSkill概念，适配Hermes工具链。
category: autonomous-ai-agents
trigger_keywords: [goskill, 目标驱动, 持续执行, 长期任务, 达标为止, 长时间运行, 复杂任务]
---

# GoSkill Pattern · 目标驱动执行

> 融合自 [AIPMAndy/goskill](https://github.com/AIPMAndy/goskill)（Apache-2.0）——不是普通「做一次就返回」，而是「围绕目标持续推进，直到满足成功标准」。

## 与 Hermes 现有工具的对比

| 维度 | delegate_task | cronjob | GoSkill Pattern |
|:----|:-------------|:--------|:----------------|
| 执行次数 | 一次 | 按计划重复 | **反复直到达标** |
| 停止条件 | 子代理返回 | 永远/限定次数 | **成功标准满足** |
| 验证机制 | 无内置 | 无内置 | **criteria check 循环** |
| 适用场景 | 一般子任务 | 定时任务 | 大型重构/分析/迁移 |

## 使用方式

### 方式 1：手动模式（推荐，零依赖）

用 `delegate_task` + 手动验证循环实现 GoSkill 模式：

```python
from hermes_tools import delegate_task, execute_code

goal = "将项目从 Android 迁移到鸿蒙"
criteria = ["compile 0 errors", "test 100% pass", "performance >= 90%"]

for attempt in range(max_attempts):
    result = delegate_task(
        goal=f"[第{attempt+1}轮] {goal}",
        context=f"上一轮结果: {last_status}",
        toolsets=["terminal", "file"]
    )
    
    # 验证标准
    verify = execute_code(f"""
    # 检查编译、测试、性能是否达标
    import json
    report = {json.dumps(result)}
    # 实际验证逻辑...
    """)
    
    if all_criteria_met:
        return report  # 达标！交付结果
    # 否则继续下一轮
```

### 方式 2：使用 goskill Python 包（需安装）

```bash
pip install -e /path/to/goskill-main
```

然后在 execute_code 中调用：

```python
from goskill import GoSkill

skill = GoSkill(
    goal="分析 1000 份财报",
    criteria={
        "coverage": ">= 90%",
        "report": "complete"
    },
    max_hours=24,
    max_attempts=10,
)

result = skill.run_with_result(my_task_func)
print(result.success, result.attempts, result.criteria_report)
```

### 方式 3：Hermes cron 循环（适合长时间自治）

用 `delegate_task` + `cronjob` 组合实现持续推进：

1. `cronjob` 每小时触发一次
2. 每次触发跑 `delegate_task` 
3. 子代理返回后检查是否达标
4. 达标 → 通知用户 + 停止 cron
5. 未达标 → 继续

## 适用场景

| 场景 | 成功标准示例 |
|:----|:------------|
| 大型代码重构 | "compile: 0 errors, test: 100% pass, lint: 0 warnings" |
| 批量文件处理 | "coverage: 1000/1000 files processed, accuracy >= 95%" |
| 深度调研 | "10 high-potential tracks identified, exec strategy complete" |
| 自动化测试覆盖 | "all 500 test cases pass, coverage >= 85%" |
| 数据迁移 | "100% records migrated, 0 integrity errors" |

## 不适用场景

- 单次问答 —— `delegate_task` 或直接对话就行了
- 模糊无标准 —— 没有可验证的 criteria 时，循环无从判断
- 实时交互任务 —— 用户等着响应时不适合走长时间循环

## 安装状态

- goskill Python 包已复制到 `/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/goskill/`
- 如果 Python 解释器导入报错，用方式 1（手动模式）代替

## 使用示例

> 「用 GoSkill 模式，帮我完成 XXX，成功标准是 YYY，最多跑 Z 小时」

示例：

```
用户：用GoSkill模式，帮我爬取并整理国内Top100 AI公司的融资数据
成功标准：
  - coverage: 100家公司
  - data_fields: 公司名/融资轮次/金额/投资方/时间
  - output: 结构化CSV
最长跑5小时

AI：好的，启动GoSkill循环：
  第1轮 → delegate_task 抓取 → 已抓45家 → 继续
  第2轮 → delegate_task 补充 → 已抓82家 → 继续
  第3轮 → delegate_task 最终补充 → 100家达标 → 交付分析报告
```
