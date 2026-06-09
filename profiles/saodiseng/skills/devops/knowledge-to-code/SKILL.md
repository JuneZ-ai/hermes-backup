---
name: knowledge-to-code
description: Turn structured knowledge from the user's Obsidian vault into executable Python tools. For when the user has notes about a domain but needs working code to USE that knowledge — not just read it.
platforms: [linux, macos]
---

# Knowledge to Code

## Trigger Conditions

Use this skill when the user asks you to DO something that your base capabilities don't support, but relevant structured knowledge already exists in the Obsidian vault.

### Detection signals

- User asks "算八字" / "排盘" / "起卦" / "算XX" (I can't natively calculate)
- User asks for a practical computation, lookup, or transformation that the vault has the rules for (formulas, tables, procedures)
- User asks "能不能做X" and the answer is "I don't natively have that" but the vault has the theory/notes

### The class-level rule

**Don't say "算不了" / "I can't."** Say: "let me check what I have to build this."

The user's philosophy is "以行入知" (act your way into knowing). Apply this to yourself: assess what you DO have (vault knowledge + Python + available libraries), and BUILD the missing piece.

## Core Workflow

### Step 1: Audit the vault

Check what the user already has in the vault before deciding what to build.

```python
# Check vault for domain notes
search_files(pattern="*", path="/mnt/c/Users/.../Obsidian Vault/六韬易哲", target="files")
# Read the key reference notes to extract:
# - Lookup tables (天干地支, 纳甲, 六十四卦, etc.)
# - Algorithm rules (生克制化, 顺逆排, 五鼠遁, etc.)
# - Logic conditions (格局判断, 喜忌, etc.)
```

### Step 2: Identify the hard computation gap

Most traditional Chinese metaphysics systems have one hard part that requires either:
- Calendar/astronomical calculation (万年历, 节气): use the `lunar-python` library
- Comprehensive lookup tables (64卦, 纳甲): embed as Python dicts from vault notes

For anything that needs astronomical/calendar math: **use lunar-python**. For pure lookup tables: **hardcode from the vault notes**.

### Step 3: Write the tool

Structure:
1. All static table data at module level (dicts/lists copied from vault notes)
2. Helper functions for each logical unit (十神, 旺衰, 纳甲, 六亲)
3. A main compute function that takes user inputs and returns structured data
4. An output formatter that presents results clearly
5. A `if __name__ == "__main__"` block with argparse CLI

### Step 4: Create unified entry point

Build a `tools.py` that dispatches to sub-tools:

```python
# tools.py skeleton
if args.command in ("八字", "bazi"):
    from bazi import paipan
    print(paipan(args.date, args.time, args.gender, args.name))
elif args.command in ("六爻", "liuyao"):
    from liuyao import qigua
    print(qigua(values, args.question))
```

### Step 5: Handle 农历→公历 + 真太阳时

The user may give a **农历生日** (e.g. "1981年五月初五") rather than 公历. The tool expects 公历 input. When this happens:

1. Convert 农历→公历 using `lunar-python`:
   ```python
   from lunar_python import Lunar
   lunar = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)
   solar = lunar.getSolar()
   ```
2. Record both dates in the output so the user can verify.

**真太阳时 correction**: If the user provides a birth place (city), calculate the longitude correction:
   - Beijing time = 120°E. Actual longitude difference → 4 minutes per degree.
   - Jishou (吉首) ~109.7°E → (120 - 109.7) × 4 = **-41.2 minutes**
   - **CRITICAL**: Check if the correction crosses the 时辰 boundary (每两小时一个时辰). A 01:48 raw → 01:07 corrected still falls in 丑时, but if raw was 01:00 sharp → 00:19 corrected, that crosses from 丑时 into 子时.

**Always write a weipan.py** (or similar pre-processing script) when the user provides:
- 农历生日 (not 公历)
- 具体出生地 (needs 真太阳时)

This script converts the input into the format bazi.py expects, then calls paipan().

### Step 6: Write README

Include:
- Dependency requirements (`pip install lunar-python`)
- Usage examples for every sub-tool
- Output section explaining what each column/field means
- Data source references (which vault notes provided what)
- File structure

### Step 7: Delegate terminal work to 燕青

You (扫地僧) cannot run terminal commands. Delegate installation and testing to 浪子燕青:

```bash
pip install lunar-python
cd /mnt/c/Users/../Obsidian Vault/六韬易哲/tools
python3 bazi.py 1990-01-01 12:00 --gender male
python3 tools.py 六爻
```

### Step 8: Deliver the interpretation (post-tool)

Once 燕青 confirms the tool works and returns output data, your real job begins. The tool is just the 术 (technique). The user asked the question for a reason — they want **解读** (interpretation), not just raw data.

**Delivery workflow:**
1. **勘误 first**: Always check the output for edge-case errors before interpreting. In one session, I initially accepted 丙子时 but it should have been 丁丑时 (真太阳时 corrected time crossed a 时辰 boundary). Fix the script first, then interpret. Tell the user "先勘误" before proceeding.
2. **先从日主说起**: "乙木·阴木·花草之命" — establish the user's position before zooming out.
3. **五行整体先走一遍**: "木火通明但缺土" — give the macro picture.
4. **然后逐项分析**: 十神格局 → 年柱 → 月柱 → 时柱 → 大运脉络。
5. **如果发现边界错误，坦诚说明**: "先勘误：时柱应该是丁丑不是丙子" — 不要掩盖问题。交代清楚了再继续。用户信任你是因为你诚实，不是因为你全对。
6. **落到一句话**: 用一句人话收住全盘。这是刘震云式的话——糙的、实的、能记住的。例如"你有当军师的天赋，没有当将军的硬命。"
7. **最后点出调整方向**: 不是泄气，是指路。

## Communication Style for Delegation

**CRITICAL USER PREFERENCE**: When giving instructions to 燕青 or summarizing what needs to be done:

- ✅ **说人话**: Direct, concrete, imperative. "需要燕青装一个库然后跑两个脚本验证"
- ✅ **List commands plainly**: Bullet list of exact commands to run
- ❌ **No literary metaphors**: No "磨刀" / "剥花生" / "装药点火" / "递菜刀" in task instructions
- ❌ **No preamble**: Don't explain why you couldn't do it yourself. Just state what needs doing.

The user's correction was explicit: "你是要燕青具体做什么。说人话，别乱打比喻。"

This is the **task-instruction voice** — separate from the philosophical dialogue voice (which can still use metaphor and literary reference when appropriate).

## Tool Storage Convention

```
六韬易哲/tools/
├── bazi.py        # Individual domain tool
├── liuyao.py      # Individual domain tool
├── tools.py       # Unified entry point
├── README.md      # Documentation
```

## Reference Files

| File | Source | Description |
|------|--------|-------------|
| `references/bazi-liuyao-tools.md` | Original session | Full technical reference: API calls, data tables, 身强身弱 algorithm (with code format + 用神修正 + case study), 六爻起卦, 真太阳时 correction, weipan.py template |
| `references/liutao-tools-inventory.md` | Moved from `philosophical-coaching` | Tool roster with interface examples and setup instructions |

**Sibling skill:** `philosophical-coaching` covers the interpretation delivery (post-tool 解读) and philosophical dialogue around 八字/六爻 results. The interpretation workflow (Step 8 above) is also referenced there.

## Pitfalls

- ❌ **Saying "I can't" when knowledge exists in the vault** — the user will correct you with "补上" (fill the gap). Always check the vault first before stating a limitation.
- ❌ **Hand-coding hard astronomical calculations** — lunar calendar, solar terms, and daily 干支 have existed for centuries as known algorithms. Use `lunar-python` (6tail's library) rather than reimplementing from scratch.
- ❌ **Only writing the tool but not testing it** — you can't run terminal commands. Explicitly delegate testing to 燕青 with exact commands.
- ❌ **Using literary language in task instructions** — the user wants direct, concrete delegation language. Save the metaphors for philosophical dialogue.
- ❌ **Over-building** — start with what the user asked for. Don't add 紫微斗数/奇门遁甲 unless they ask. The vault may have notes on those too, but the user controls scope.
- ❌ **Ignoring 真太阳时 when the user gives 出生地** — Always correct for longitude before feeding time into bazi.py. A 41-minute difference can flip the entire 时柱 (子时↔丑时).
- ❌ **Assuming raw bazi.py output is correct** — The tool can produce wrong 时柱 if 真太阳时 correction wasn't applied. Always verify the 时辰 matches the corrected local time, especially when the time is near a 时辰 boundary (every 2 hours).
- ❌ **Delivering raw tool output without 解读** — The user doesn't want a table of data; they want someone to tell them what it means. The tool is the prep work; the interpretation is the real value.
- ❌ **Skip verification when the boundary is tight** — If 真太阳时 puts the time within 15 minutes of a 时辰 boundary, flag it to the user and explain both possibilities. Don't silently pick one.
- ❌ **Using BAGE 通用喜忌 without 身强身弱 correction** — The BAGE table stores generic喜忌 for each格局 (e.g. 伤官格喜印/财). But身强 vs 身弱 changes everything. A身弱伤官格 should 喜印/比 (水/木) not 喜印/财 (水/土), because 土财会坏印. Always run `judge_shenqiang()` before assigning用神 and override the generic BAGE with the身强/身弱-correction table (see references/bazi-liuyao-tools.md for 身强身弱 algorithm details). A wrong用神 recommendation destroys trust in the entire output.
