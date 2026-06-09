# GitHub Skill 安装指南（Hermes Agent）

当用户提供 GitHub 仓库链接要求安装技能时，使用本模式。

## 安装路径
所有用户技能放在：`~/.hermes/skills/<category>/<skill-name>/`

常用分类：
- `autonomous-ai-agents/` — 自主Agent相关（女娲、达尔文等）
- `creative/` — 设计/创作类（花叔设计等）
- `productivity/` — 生产效率类（喂料管道等）

## 安装步骤

### Step 1: 探索仓库结构
```bash
curl -sL --max-time 15 -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/<owner>/<repo>/contents"
```
输出JSON数组，遍历 `type` 和 `name`。注意有些仓库有嵌套子目录。

### Step 2: 定位 SKILL.md
SKILL.md 可能在多级嵌套中：
```
repo/
  browser-automation/
    chrome-devtools-mcp/
      SKILL.md       ← 在这
```
在第二级 `contents` API 调用中定位。

### Step 3: 下载 SKILL.md
```bash
curl -sL --max-time 15 -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/<owner>/<repo>/contents/<path>/SKILL.md" \
  | python3 -c "import sys,json,base64; d=json.load(sys.stdin); open('/dev/stdout','wb').write(base64.b64decode(d['content']))" \
  > /home/hermes/.hermes/skills/<category>/<skill-name>/SKILL.md
```

### Step 4: 修复 Frontmatter
如果 SKILL.md 的 YAML frontmatter 使用多行 `description: |` 格式，Hermes 的 `skill_view` 可能无法加载。修成单行：
```yaml
# 改成：
description: "...（全文合并为一行）"
```
由空格/无空格分隔均可，关键在于不能有 `|` 换行。

### Step 5: 下载支持文件
- `references/` — 使用相同API模板下载
- `scripts/` — 同上
- `templates/` — 同上

### Step 6: 安装npm依赖（如需要）
```bash
npm install -g <package-name>
```

### Step 7: 验证加载
```bash
# 注意：短名可能在 skills_list 中可见但 skill_view 无法加载
# 可能需要用全路径 category/skill-name 加载
skill_view(name="<category>/<skill-name>")  # 或
skill_view(name="<skill-name>")
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `skills_list` 有但 `skill_view` 404 | YAML frontmatter 多行描述 | 改为单行 `""` |
| `git clone` 超时 | WSL 网络限制 | 改用 GitHub API 逐文件下载 |
| SKILL.md 内容为空 | API 返回非 UTF-8 编码 | 用 `base64.b64decode()` 再 decode |
| 第三方安装失败 | npm 未安装/版本过旧 | `npm install -g npm` 后重试 |
