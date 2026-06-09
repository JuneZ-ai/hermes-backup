---
name: maintenance-governance
description: 系统维护治理规则——工具/包/应用的安装、更新、卸载必须遵循备份→通知→确认→执行→验证的正交流程。
version: 1.0.0
---

# 系统维护治理规则

## 核心原则：备份 → 通知 → 确认 → 执行 → 验证

**所有涉及系统现有工具的变更操作**（npm/pip/binary 等包管理器的安装、更新、卸载、升级），必须遵循以下五步流程，不得自动执行。

## 五步流程

### Step 1 · 备份当前状态

在做出任何变更前，记录当前版本信息：

```bash
# 标准备份格式
tool_name --version > backup/<tool-name>-backup-v<old-version>.txt
# 可选：补充更多元信息
npm view <package> --json >> backup/<tool-name>-backup-v<old-version>.txt
```

备份文件保存到 `~/.hermes/scripts/` 或项目相关的 `backup/` 目录。

### Step 2 · 通知用户

通知内容必须包含：
- 当前版本 → 目标版本
- 变更类型（安装 / 更新 / 卸载 / 降级）
- 备份位置
- 明确的确认请求（如"回复：更新 xxx"）

### Step 3 · 等待确认

**不要假设用户同意。** 必须等到用户明确回复确认指令（如"更新"、"升级"、"go ahead"等），才能执行。用户沉默或转换话题视为暂停，不在后台偷偷执行。

### Step 4 · 执行变更

确认后执行变更。优先使用包管理器的标准命令：

```bash
npm install -g <package>     # npm 包
pip install -U <package>     # pip 包
```

### Step 5 · 验证结果

执行后必须验证新版本：

```bash
tool --version    # 确认版本号正确
tool --help       # 确认命令可用（可选）
```

向用户报告：旧版本 → 新版本 + 备份位置。

## 看门狗巡检模式（只检测，不执行）

对于需要定期巡检的工具，使用 `no_agent=True` watchog 脚本 + cron 排期：

```bash
#!/bin/bash
# 脚本放在 ~/.hermes/scripts/ 下，cronjob 传相对路径
# 获取当前版本
CURRENT=$(<tool> --version 2>/dev/null | grep -oP '[\\d]+\\.[\\d]+\\.[\\d]+')
# 获取最新版本（npm 或 GitHub releases）
LATEST=$(npm view <package-name> version 2>/dev/null)

if [ -z "$CURRENT" ] || [ -z "$LATEST" ]; then
    exit 0
fi

if [ "$CURRENT" != "$LATEST" ]; then
    echo "🔔 <tool-name> 有新版本"
    echo "当前版本：$CURRENT"
    echo "最新版本：$LATEST"
    echo "如需更新，请回复：更新 <tool-name>"
    exit 0
fi
# 无更新 → 静默退出，不投递消息
exit 0
```

脚本职责：比较当前版本 vs npm/pip 最新版本
  有更新 → 输出通知消息（用户看到后可在对话中要求手动更新）
  无更新 → 静默退出（无消息投递）
**决不：在脚本中执行更新**

注册定时任务：

```python
cronjob(
    action="create",
    name="工具名 版本巡检",
    schedule="0 9 */5 * *",  # 每5天早9点
    script="check-<tool>-update.sh",  # 相对 ~/.hermes/scripts/
    no_agent=True
)
```

参见 `references/lark-cli-implementation.md` 的 lark-cli 实现作为参考范例。

## 常见陷阱

- ❌ 不要在巡检脚本中直接执行更新 —— 永远等用户确认
- ❌ 不要假设 npm registry 一定有 version 命令 —— 有些包走 GitHub releases
- ❌ 不要用 `read_file` 读 `config.yaml` 取 API key —— hex dump（`od -c`）才能拿到完整值
- ⚠️ `read_file` 和 `terminal` 中的 `cat`/`grep` 会截断 API key（`***` 或 `sk-xxx...xxx` 模式）

## 适用范围

| 操作类型 | 适用 | 不适用 |
|----------|------|--------|
| npm 全局包升级 | ✅ 必须走五步 | — |
| pip 包升级 | ✅ 必须走五步 | — |
| 系统包管理器（apt/brew） | ✅ 必须走五步 | — |
| 首次安装（新工具） | ✅ 通知用户即可（无需备份） | — |
| pip install 在 venv 内 | — | ❌ 不适用（venv 是项目级的，不影响全局） |
| 测试环境/沙箱 | — | ❌ 不适用 |
| 用户明确要求"直接更新" | — | ❌ 跳过备份通知 步骤，但仍需验证 |

## 用户原话（来源：2026-05-29）

> "以5天为单位，巡检一次，做更新。更新之前做好备份，并且要通知我，我确认后才能正式安装。我不说，你的工作机制里也有这一条吗？"
>
> 答：没有。这就是新规则。
