---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [writing-plans, requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range.

## 渐进式信息架构（Recommended Pattern）

受 TeachAny v7.x 启发，复杂 skill 应采用**「轻摘要 + 卫星文档」**架构：

```
skills/<category>/<name>/
├── SKILL.md                 # 决策骨架（只留关键路径，建议 150-300 行）
├── RULES.md                 # 硬规则（可选，见下方说明）
├── references/              # 基线规则、设计决策、背景知识
├── guides/                  # 使用指南、最佳实践
├── phases/                  # 按阶段展开的完整工作流
├── templates/               # 模板文件（代码骨架、manifest、配置）
├── scripts/                 # 辅助脚本（验证、生成、转换）
└── tech/                    # 技术实现细节、API参考
```

**核心原则：**

- **SKILL.md 是导航页，不是百科全书。** 只放决策路径和关键步骤。细节按需读取卫星文档。
- **一个卫星文档解决一个关注点。** `references/baseline-rules.md` 放基线规则，`phases/deploy.md` 放部署流程，`guides/pbl.md` 放 PBL 设计指南。
- **文件名自解释。** 看目录结构就知道这个 skill 覆盖了哪些维度。
- **卫星文档也要有 frontmatter。** 至少包含 `purpose` 字段说明文档用途。

### 何时拆分

| SKILL.md 体积 | 建议 |
|--------------|------|
| < 10k chars | 单文件，不拆分 |
| 10-20k chars | 考虑将「常见陷阱」和「参考表格」拆到 `references/` |
| 20-50k chars | 必须拆分。工作流拆到 `phases/`，参考拆到 `references/` |
| > 50k chars | 严重超标。重构为向导式结构 |

拆分后 SKILL.md 应像一份**目录**：每个卫星文档在 SKILL.md 中有1-2行说明+链接，让读者知道什么情况下该读哪个文件。

### RULES.md — 硬规则文件（可选）

当 skill 包含不可违反的纪律时，把硬规则抽到独立的 `RULES.md`：

```
# <Skill Name> 硬规则

本文件只保留最终有效规则。

## A. 执行纪律

- **#1** **闭环验证**：声称完成/修复前必须运行实际命令或浏览器验证，并给出关键输出。
- **#2** **失败两次换方案**：同一方向连续失败 2 次，切换本质不同路径。
- **#3** **一类问题一起扫**：修一个模块后检查同类问题是否在别处也存在。
- **#4** **不绕过质量闸门**：除非用户明确要求紧急跳过，否则不得跳过验证。

## B. 内容规范

- **#5** [具体规则]
- **#6** [具体规则]
```

规则编号（#1, #2, ...）方便在对话和日志中精准引用。规则必须**可执行**——不是「要注意质量」，而是「声称完成前必须跑通验证脚本」。

### 「无捷径」原则

如果 skill 中定义了基线项（必须完成的步骤），**不允许跳过某些项声称「后续升级」**。唯一可以豁免的情形：

- 某项依赖外部资源，在当前网络环境下反复尝试（≥2 次，每次间隔 ≥30 秒）确实无法连接
- 且无本地替代方案
- 且交付说明中明确注明：豁免原因 + 尝试次数 + 后续补齐步骤

不构成豁免理由：
- 「用户只是想先看看效果」
- 「先做简版，之后再补」
- 「这个功能感觉用不上」
- 任何主观判断或时间压力

## Peer-Matched Structure

### 单文件模式（< 10k chars）

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

### 渐进式多文件模式（≥ 10k chars）

参考上方「渐进式信息架构」章节。SKILL.md 作为导航页时，应在底部加一个**文件索引**：

```
## Skill 文件索引

| 文件 | 用途 | 何时读 |
|------|------|--------|
| `RULES.md` | 硬规则与执行纪律 | 每次执行前 |
| `phases/workflow.md` | 完整分阶段工作流 | 需要执行完整流程时 |
| `references/api.md` | API 参考 | 调试/参数配置时 |
| `guides/pbl.md` | 项目式学习设计指南 | 设计 PBL 课件时 |
| `templates/course-skeleton.html` | 课件骨架模板 | 创建新课件时 |
```

索引让读者（包括未来的自己和其它 agent）能在 10 秒内找到需要的部分。

---

完整的架构参考案例见 `references/skill-architecture-patterns.md`（含 TeachAny v7.x 完整目录分析、RULES.md 模板、职责拆分表）。

> 📖 实战案例：2026-05-31 对 WorkBuddy 两个巨型 skill（六韬易哲 139KB、六韬智脑 68KB）进行渐进式重构，分别压缩 23x 和 15x。详见 [`references/wb-skill-distillation-case-study.md`](references/wb-skill-distillation-case-study.md)。

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **Always commit** the edit — in-repo skills are source, not runtime state.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

8. **SKILL.md 长得像百科全书而不像导航页。** 如果你在 SKILL.md 里塞了超过 20k 字符的工作流步骤，说明该拆分了。把完整步骤移到 `phases/` 或 `references/`，SKILL.md 只留决策路径。

9. **没有 RULES.md 但有大量「不可以」「必须」「禁止」。** 如果你在 SKILL.md 里反复强调纪律，说明需要一个独立的 `RULES.md`。把不可违反的规则抽出去，SKILL.md 专注于「做什么」。

10. **卫星文档职责混杂。** `phases/` 里放设计哲学，`guides/` 里放硬性规则，`references/` 里放流程步骤。每个目录解决一个关注点，不要混放。

11. **允许「快速模式」/「先做简版」绕过基线。** 如果 skill 定义了基线项，必须严格执行。允许跳过等于允许 skill 失效。参考 TeachAny 的「没有快速模式」原则。

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8-15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch
