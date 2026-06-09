# 模块目录改名跨库通用工作流

> 教训案例：六韬道史 → 六韬史鉴（2026-05-28）
>
> 原模块名「道史」字面意思好但发音有歧义（dào shǐ ≈ 道士/倒屎）。用户要求全局改名。

## 改名前三问（韬定律元操作原则检查）

1. **做对的事 > 做更多的事** — 这个改名值得做吗？还是留给时间？
2. **改变连接方式 > 加新节点** — 改名是最优解，还是有更好的路？
3. **修三次还不好 → 换维** — 这个名字被抱怨过几次了？

## 执行步骤

### Phase 1：文本替换（先于目录改名）

**顺序不可颠倒**：先替换文本内容，再改目录名。否则链接全断。

```bash
# Step 1 — 全库 sed 替换 vault 内所有 .md 文件
cd "/mnt/c/Users/18502/Documents/Obsidian Vault/"
find . -name "*.md" -not -path "./.obsidian/*" -exec sed -i 's/旧名/新名/g' {} +

# Step 2 — 跨系统同步到 Hermes skills
find /home/hermes/.hermes/skills/ -name "*.md" -exec sed -i 's/旧名/新名/g' {} +
```

### Phase 2：处理残余独立引用

sed 只替换「旧名」作为子串的部分，不替换独立词汇的引用。需追加针对性替换：

常见残余模式：
```
「主干（旧名）」 → 「主干（新名）」
「旧名以鉴观世」 → 「新名以鉴观世」
「旧名是这棵树的主干」 → 「新名是这棵树的主干」
「在旧名」 → 「在新名」
「旧名·/旧名—/旧名，」 → 「新名·/新名—/新名，」
```

用 patch 逐个修复，或在 sed 中添加更多模式一次性处理。

### Phase 3：目录重命名

```bash
mv "六韬旧名" "六韬新名"
```

### Phase 4：更新索引文档

1. 总纲（`00-六韬总纲.md`）— 树形图 + 模块名 + 使用场景
2. 子模块总纲 — 更新 title/tags/aliases
3. 分类仲裁树（SCHEMA）
4. 决断之桥索引
5. 架构提案文档

### Phase 5：更新别名

在总纲文件 frontmatter 的 `aliases` 列表新增新名别名，保留旧名别名作为向后兼容入口。

## 关键陷阱

| 陷阱 | 说明 | 对策 |
|:----|:-----|:-----|
| **workspace.json** | Obsidian 缓存文件存旧路径 | **不要改它**，关闭 Obsidian 后自动重建 |
| **tags 保留** | `tags:` 中的旧名可以不改 | 保留搜索可达性，不影响显示 |
| **filename 保留** | 如 `DS-00-道史总纲.md` 不改名 | Obsidian wikilink 基于 filename 非路径。目录改名后完整路径 `[[六韬新名/DS-00-旧名总纲.md]]` 仍能解析 |
| **skill 文件中的 Obsidian wikilink** | `[[模块/文件|别名]]` 格式在 skill 中不渲染 | 改纯文本引用，或删除 wikilink 语法 |
| **ASCII 艺术图** | 树形图中的模块名是固定字符串，sed 可能漏掉 | 扫描 `鉴 · 旧名`、`主干 · 旧名` 等 ASCII art 模式 |

## 验证命令

```bash
# Vault 内无残留（排除 tag/alias）
grep -rn "旧名" --include="*.md" . | grep -v ".obsidian" | grep -vE "(tags:|aliases:)"
# Skills 层无残留
grep -rn "旧名" /home/hermes/.hermes/skills/ --include="*.md" --include="*.py"
```
