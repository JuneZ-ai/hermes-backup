# 飞书 CLI 安装与 OAuth 授权

> 当需要枚举用户**个人云盘目录树**（而非仅读取已知token文档）时使用 lark-cli。本文件覆盖：安装 → 绑定 → 两轮OAuth → 枚举 → 下载/导出 → 入库。

## 流程图

```
安装 CLI (npm i -g @larksuite/cli)
  → 安装 SKILL (npx skills add ...)
  → 绑定应用 (config bind --identity user-default)
  → 第1轮OAuth (login --recommend) → 基础scopes
  → 第2轮OAuth (login --domain drive) → 补充space:document:retrieve
  → 枚举个人空间 (drive files list --as user --page-all)
  → 下载/导出文件 (drive +download / +export)
  → 按 obsidian-ingestion-pipeline 入库
```

## 第1步：安装

```bash
npm install -g @larksuite/cli
# 验证
lark-cli --version

# 安装CLI SKILL（必需——让CLI感知Hermes上下文）
npx -y skills add https://open.feishu.cn --skill -y
```

## 第2步：绑定应用凭证

lark-cli 需要绑定到已有的 Hermes 飞书应用（不要创建新应用）：

```bash
lark-cli config bind --source hermes --identity user-default
```

**身份模式选择：**
| 模式 | 能做什么 | 不能做什么 |
|:----|:--------|:---------|
| `bot-only` | 操作Bitable、发消息、读文档（已知token） | ❌ 不能访问个人云盘、日历、邮件 |
| `user-default` | 以上全部 + ✅ 个人云盘/日历/邮件 | 需要用户OAuth授权 |

**目标情况**：如需枚举用户个人空间目录树，必须选用 `user-default`。

> ⚠️ `config init --new` 在 Hermes 上下文中被拦截（会创建并行应用导致冲突）。必须用 `config bind` 绑定现有应用。

## 第3步：OAuth 授权（两轮）

### 第1轮：基础 scopes（--recommend）

```bash
# 生成授权二维码（不阻塞）
lark-cli auth login --no-wait --json --recommend
```

输出包含 `verification_url` 和 `device_code`。生成二维码并发送给用户扫码：

```bash
lark-cli auth qrcode "<verification_url>" --output feishu_auth_qr.png
```

用户扫码授权后，用 device_code 完成登录：

```bash
lark-cli auth login --device-code "<device_code>"
```

授权成功后输出包含：`userName`、`userOpenId`、expires 等信息。

### 第2轮：Drive 相关 scopes（--domain drive）

枚举用户个人空间需要 `space:document:retrieve` scope，它不在 `--recommend` 范围内，必须单独申请：

```bash
# 生成第二轮授权链接
lark-cli auth login --no-wait --json --domain drive
```

重复 生成二维码 → 用户扫码 → `--device-code` 完成。

**第二轮新增 scopes：**
- `space:document:retrieve` — 枚举用户个人空间文件
- `search:docs:read` — 搜索文档

## 第4步：枚举用户个人空间

```bash
# 根目录
lark-cli drive files list --as user --page-all --format json

# 子文件夹
lark-cli drive files list --as user --page-all \
  --params '{"folder_token":"<folder_token>"}' --format json
```

**关键参数：**
- `--as user` — 使用用户身份（否则只有 bot 身份）
- `--page-all` — 自动翻页获取全部
- `--format json` — JSON输出（可配合 `--jq` 过滤）

**输出字段：** `name`, `token`, `type` (file/docx/doc/sheet/folder/bitable), `parent_token`, `url`, `owner_id`, `created_time`, `modified_time`

## 第5步：下载/导出文件

### PDF/二进制文件（用 +download）

```bash
# file类型（PDF/图片/zip等）
cd /home/hermes && lark-cli drive +download \
  --as user --file-token "<token>" --output 文件名.pdf --overwrite
```

> ⚠️ `--output` 必须是**相对路径**（不能用绝对路径）。先 `cd` 到目标目录再执行。

### docx/文档（用 +export 转 markdown）

```bash
cd /home/hermes && lark-cli drive +export \
  --as user --token "<token>" --doc-type docx \
  --file-extension markdown --file-name "笔记标题" --overwrite
```

> `+download` 仅适用于 `file` 类型（PDF等）。docx 必须用 `+export` 转换。

### 验证导出

```bash
wc -l 文件名.md
head -60 文件名.md  # 查看前60行判断内容完整性
```

## 第6步：批量入库

获取文档后，按 `obsidian-ingestion-pipeline` 的标准流程处理：

1. 创建 `_raw_sources/articles/` 或相应路径的原始素材归档
2. 根据内容确定模块归属（六韬智脑/太极双螺旋/六韬史鉴/实战案例等）
3. 创建笔记（YAML frontmatter + 结构化提炼 + 关联已有笔记）
4. 更新 `00-六韬总纲.md`（模块地图 + 模块计数 + 使用场景）
5. 注入反向链接（至少2条外部链接）
6. 同步飞书三表（搭建日志 + 每日记录）

## 验证状态

```bash
# 确认授权状态
lark-cli auth status --format json
# 关键字段：identity (user), userName, tokenStatus (valid), expiresAt, scope

# scope 中必须包含的关键权限：
# - drive:drive.metadata:readonly  ← 浏览云盘
# - space:document:retrieve       ← 枚举个人空间文件
# - drive:file:download           ← 下载文件
# - docx:document:readonly        ← 读取文档内容
```

## 已知陷阱

| 陷阱 | 现象 | 对策 |
|:----|:-----|:-----|
| `+download` 对 docx 返回 404 | download failed: HTTP 404 | 用 `+export` 替代，`+download` 只支持 `file` 类型 |
| `+download` 拒绝绝对路径 | unsafe output path | 先 `cd` 到目标目录，用 `./文件名` 相对路径 |
| 缺少 `space:document:retrieve` | drive files list 报 permission denied | 第2轮 OAuth 用 `--domain drive` |
| 旧进程残留 | 之前用 `--token` 而非 `--file-token` 启动的下载进程超时失败 | 忽略，用正确参数重跑。每次重启会作废上一轮的 device code |
| token 过期 | auth status 显示 tokenStatus: expired | 用 `lark-cli auth login` 重新授权 |

## 更多

- lark-cli 版本：1.0.41（当前环境）
- 授权有效期：2小时（access_token）+ 7天（refresh_token 自动刷新）
