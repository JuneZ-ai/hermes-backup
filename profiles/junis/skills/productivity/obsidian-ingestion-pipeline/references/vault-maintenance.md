# Vault 架构维护 · 批量规范化脚本模板

## 场景：批量统一 frontmatter 格式

当 vault 内存在多种 frontmatter 混用时（内联 tags、哈希 tags、YAML list tags 混杂），执行以下流程。

### Python 规范化脚本

```python
"""
Batch normalize all frontmatter in the vault:
1. tags: [a,b] → tags:\n  - a\n  - b
2. tags: #a #b → tags:\n  - a\n  - b
3. Ensure field ordering: title → tags → aliases → created → ...
4. Add created field if missing (from date field)
"""
import os
import yaml
import re
from pathlib import Path

VAULT = Path("/mnt/c/Users/18502/Documents/Obsidian Vault")
SKIP_DIRS = {'.trash', '.obsidian'}
SKIP_FILES = {'00-喂料模板.md'}  # 模板用 {{date}} 占位符，YAML 解析会报错

# 字段顺序
FIELD_ORDER = ['title', 'tags', 'aliases', 'type', 'created', 'updated', 'date', 
               'status', 'version', 'module', 'creator', 'source', 'cssclass']

def normalize_frontmatter(content: str) -> tuple[str, bool]:
    m = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not m:
        return content, False
    
    raw_yaml = m.group(1)
    changed = False
    
    try:
        fm = yaml.safe_load(raw_yaml)
    except:
        return content, False
    if not isinstance(fm, dict):
        return content, False
    
    # Fix 1: tags → YAML list
    if 'tags' in fm:
        tags = fm['tags']
        if isinstance(tags, str):
            if tags.startswith('#'):
                tag_list = [t.lstrip('#') for t in tags.split() if t]
            else:
                tag_list = [t.strip() for t in tags.replace(',', ' ').split() if t]
            fm['tags'] = tag_list
            changed = True
        elif isinstance(tags, list):
            new_tags = []
            for t in tags:
                if isinstance(t, str) and t.startswith('#'):
                    new_tags.append(t.lstrip('#'))
                    changed = True
                else:
                    new_tags.append(t)
            if changed:
                fm['tags'] = new_tags
    
    # Fix 2: aliases → list
    if 'aliases' in fm and isinstance(fm['aliases'], str):
        aliases = fm['aliases']
        if re.search(r'[,，]', aliases):
            fm['aliases'] = [a.strip() for a in re.split(r'[,，]', aliases) if a.strip()]
        else:
            fm['aliases'] = [aliases]
        changed = True
    
    # Fix 3: inherit created from date
    if 'created' not in fm and 'date' in fm:
        fm['created'] = fm['date']
        changed = True
    
    # Rebuild with consistent ordering
    new_fm = {}
    for field in FIELD_ORDER:
        if field in fm:
            new_fm[field] = fm[field]
    for k, v in fm.items():
        if k not in new_fm:
            new_fm[k] = v
    
    if new_fm == fm and not changed:
        return content, False
    
    # Write new frontmatter
    lines = ['---']
    for k, v in new_fm.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif v is None:
            pass
        else:
            lines.append(f"{k}: {v}")
    lines.append('---')
    
    rest = content[m.end():]
    return '\n'.join(lines) + '\n' + rest, True

# Execute
for root, dirs, files in os.walk(VAULT):
    rel = Path(root).relative_to(VAULT)
    if set(rel.parts) & SKIP_DIRS:
        continue
    if rel.name.startswith('.'):
        continue
    
    for f in sorted(files):
        if not f.endswith('.md') or f in SKIP_FILES:
            continue
        fp = Path(root) / f
        content = fp.read_text(encoding='utf-8')
        new_content, changed = normalize_frontmatter(content)
        if changed:
            fp.write_text(new_content, encoding='utf-8')
            print(f"Fixed: {fp.relative_to(VAULT)}")
```

### 修复因 YAML `#` 注释导致丢失的 tags

一些总纲笔记的 `tags` 字段使用 `tags: #tag1 #tag2` 格式，YAML 解析器将其视为注释，导致 `tags` 字段被设为 null。需要手动补回：

```python
fixes = {
    "00-六韬总纲.md": {"tags": ["六韬", "总纲", "MOC"]},
    "太极双螺旋/00-太极双螺旋总纲.md": {"tags": ["太极双螺旋", "元认知", "底层框架", "思维操作系统"]},
    # ... 每个丢失 tags 的笔记
}
```

读取受影响文件后用 yaml.safe_load 验证 tags 是否为空，按 `fixes` 字典恢复。

### 修复中文字段名的旧笔记

早期笔记使用了中文 YAML key：

| 中文 | 英文 |
|------|------|
| 创建日期 | created |
| 更新日期 | updated |
| 标题 | title |
| 标签 | tags |
| 关联 | links |
| 来源 | source |
| 作者 | creator |
| 版本 | version |
| 状态 | status |

处理方式：从旧 frontmatter 提取值，映射到英文 key，重建 frontmatter。保留旧笔记的 body 不变。

### 验证脚本

```python
"""
Final validation — scan all notes for:
- YAML parse errors
- Inline tags (not list format)
- Missing title field
- Double frontmatter markers
"""
import os, yaml, re
from pathlib import Path

VAULT = "/mnt/c/Users/18502/Documents/Obsidian Vault"
issues = []
count = 0

for root, dirs, files in os.walk(VAULT):
    if '.trash' in root or '.obsidian' in root:
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        count += 1
        fp = Path(root) / f
        content = fp.read_text('utf-8')
        
        m = re.match(r'^---\n(.*?)---\n', content, re.DOTALL)
        if not m:
            continue
        
        try:
            fm = yaml.safe_load(m.group(1))
        except:
            if f != '00-喂料模板.md':  # template uses {{date}}
                issues.append(f"YAML error: {Path(root).name}/{f}")
            continue
        
        if not isinstance(fm, dict):
            continue
        if 'title' not in fm:
            issues.append(f"No title: {Path(root).name}/{f}")
        if 'tags' in fm and isinstance(fm['tags'], str):
            issues.append(f"Inline tags: {Path(root).name}/{f}")

print(f"Scanned: {count} notes")
print(f"Issues:  {len(issues)}")
if issues:
    for i in issues:
        print(f"  • {i}")
```

## 场景：序号冲突修复及链接同步

当同一目录下两个笔记共享同一序号前缀（如 `13-百年孤独.md` 和 `13-华盛顿石碑.md` 都在 `六韬史鉴/`）：

### 冲突检测

```bash
ls "六韬史鉴/" | grep -oP '^\d+' | sort | uniq -d
```

若有输出（如 `13`、`14`），说明存在序号冲突。

### 修复步骤

1. **重命名文件** — 后创建的笔记跳至下一个空闲序号：
   ```bash
   cd vault/六韬史鉴
   mv "13-百年孤独·孤独的七种形态.md" "16-百年孤独·孤独的七种形态.md"
   ```

2. **确定空闲序号** — `ls | grep -oP '^\d+' | sort -n` 看哪个数字缺失

3. **扫描所有引用旧路径的笔记**（包括总纲、桥笔记、关联阅读、frontmatter中的aliases）：
   ```bash
   rg '13-百年孤独' vault/ -l
   ```

4. **逐一 patch 每条引用**，注意三种引用形式：
   - 完整路径：`[[六韬史鉴/13-百年孤独·孤独的七种形态|百年孤独]]`
   - 短路径：`[[13-百年孤独]]`
   - 文本引用：`史鉴/13-百年孤独`
   - 总纲模块树中的行
   - 总纲使用场景中的 `\\` 转义引用

5. **更新总纲计数** — 若模块是「六韬史鉴 | N 篇」，数字不变（篇数没变），但总纲树形展示需要修正

6. **给新文件名加 internal [[wikilink]] 自印证** — 在笔记正文中找到一个提到自身的位置（如知识库定位图），把自引用更新为新路径

### 易漏点

- 总纲的使用场景表中，路径含 `\\` 转义（Obsidian 表格格式），搜索时用 `13-百年孤独` 而非完整 `[[路径`
- 桥笔记的关联阅读列表可能引用旧路径
- 新建的精要笔记自身 frontmatter 如果有 `aliases` 指向旧序号，不需要修改（alias 只用于搜索，不用于链接解析）
- 百年孤独类文学笔记的「知识库定位」ASCII 图中会引用自身文件名，也需要更新

### 预防

创建新笔记前用 `ls 目录/ | grep -oP '^\d+' | sort -n` 检查所有已用序号，取最大序号+1。

## 场景：收件箱净化

收件箱 `01-信息流/` 只应包含素材笔记（`status: raw/processed`）和 `00-喂料模板.md`。

发现非素材文件（如 `01-知识图谱总览.md` 这类索引），移出到对应模块目录。

```bash
cp vault/01-信息流/XX笔记.md vault/MOC地图/XX笔记.md
rm vault/01-信息流/XX笔记.md
```

检测命令：
```bash
ls -la "vault/01-信息流/"
# 如果看到 01-* 以外的序号前缀文件，可能是非素材索引
```

## 场景：重复文件合并

当 cron 和手动处理分别创建了同源不同名的素材文件时：

1. **保留先创建的文件**（保持创建日期和已建链接）
2. **合并 frontmatter** — 取更新的格式（YAML list > inline, processed > raw）
3. **合并/去重 content** — 取更完整的版本
4. **删除后创建的副本**
5. **更新所有 [[链接]] 指向到保留文件**

```python
# 合并示例
old_file = vault / "01-信息流/原版名.md"  # 保留
new_file = vault / "01-信息流/新版名.md"  # 删除

# 1. 读 new_file 的 content，检查是否有 old_file 没有的段落
# 2. 更新 old_file status = processed
# 3. 删除 new_file
# 4. 更新所有已有 [[新版名]] → [[原版名]]
```

## 适用时机

- 用户说"帮我整理笔记格式"、"统一一下frontmatter"
- 发现 vault 内存在多种 frontmatter 格式
- 批量新建笔记后（5+篇）
- 收件箱混入了非素材文件
