# 六韬易哲 · 理法工具清单

> Vault path: `六韬易哲/tools/` under the Obsidian vault root.

## Tool roster

| Tool | Purpose | Dependency | Vault data sources |
|------|---------|-----------|-------------------|
| `bazi.py` | 八字排盘 — Gregorian date → 四柱 + 十神 + 旺衰 + 五行 | `lunar-python` | 八字命理/01-四柱基础, 02-十神体系, 03-旺衰十二宫 |
| `liuyao.py` | 六爻起卦 — coin toss → 本卦 + 之卦 + 纳甲 + 六亲 + 六神 + 世应 | None | 易经体系/05-六爻纳甲, 06-断易心法 |

## How scripts are structured

Each script follows the same pattern:
1. All lookup tables (天干/地支/五行/十神/十二宫/纳甲) as module-level dicts
2. Pure-function helpers that map input → output
3. A single `qigua()` or `paipan()` entry function
4. An `if __name__ == "__main__":` block with argparse
5. CLI output uses box-drawing characters (╔╗╚╝┌┐└┘)

## Setup needed

```bash
pip install lunar-python   # required for bazi.py only
```

## Interface examples

```bash
python bazi.py 1990-01-01 12:30 --gender male --name 张三
python liuyao.py --question 最近工作如何
python liuyao.py 789889     # manual input: 初爻到上爻
```
