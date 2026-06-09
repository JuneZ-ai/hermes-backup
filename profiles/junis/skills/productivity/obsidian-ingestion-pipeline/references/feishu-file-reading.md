# 飞书 Cloud Drive 文档读取方法

> **补充**：如需枚举用户个人云盘目录树（而非已知token读内容），参照 `references/feishu-cli-setup.md` 安装飞书 CLI 并完成 OAuth binding。

# 飞书 Cloud Drive 文档读取方法

本文件覆盖**直接通过 Raw API 读取已知文档**。如需**枚举目录树 + 批量下载/导出**（lark-cli 方法），见 `references/feishu-cli-setup.md`。

## 两种方法的选择

| 场景 | 方法 | 参考文件 |
|:----|:----|:---------|
| 已知token单篇读取 | Raw API（本文件） | 下文 |
| 枚举目录树/批量处理 | lark-cli | `references/feishu-cli-setup.md` |
| 自动喂料入库 | 完整pipeline | SKILL.md 主文件 |

## 识别文档类型

| 链接模式 | 文档类型 | 读取API |
|---------|---------|---------|
| `/docx/` | 新版文档 | `GET /open-apis/docx/v1/documents/{id}/raw_content` |
| `/file/` | Drive 文件（PDF/文本/图片） | `GET /open-apis/drive/v1/files/{token}/download` |
| `/sheet/` | 电子表格 | 通过 bitable/sheet API |
| `/base/` | 多维表格（Bitable） | `POST /open-apis/bitable/v1/apps/{token}/tables/{table_id}/records/search` |
| `/wiki/` | 知识库页面 | `GET /open-apis/wiki/v2/spaces` |

## 核心工作流

### 1. 获取 tenant_access_token

```python
import requests
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET},
    timeout=10
)
token = resp.json()["tenant_access_token"]
```

### 2. 读取 docx 文档内容（最常用）

```python
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
doc_token = "提取自URL的24位token"

resp = requests.get(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/raw_content",
    headers=headers,
    timeout=15
)
# 返回: {"code": 0, "data": {"content": "纯文本..."}}
content = resp.json()["data"]["content"]
```

### 3. 获取文档元信息

```python
resp = requests.post(
    "https://open.feishu.cn/open-apis/drive/v1/metas/batch_query",
    headers=headers,
    json={"request_docs": [{"doc_token": doc_token, "doc_type": "docx"}]},
    timeout=15
)
meta = resp.json()["data"]["metas"][0]
# 包含: title, create_time, latest_modify_time, owner_id, doc_type
```

### 4. 列出云盘根目录文件

```python
resp = requests.get(
    "https://open.feishu.cn/open-apis/drive/v1/files?page_size=50&order_by=EditedTime",
    headers=headers,
    timeout=15
)
files = resp.json()["data"]["files"]
# 每个文件: {name, token, type(bitable/docx/sheet/file/folder), parent_token, url}
```

### 5. 获取文档结构化内容（块级）

```python
resp = requests.get(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks",
    headers=headers,
    timeout=15
)
blocks = resp.json()["data"]["items"]
# 每个block有 block_type（段落/标题/表格等）+ content 字段
# 适用于需要保留文档结构（而非纯文本）的场景
```

### 6. 检查文档权限（公开/租户可见性）

```python
resp = requests.get(
    f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/public?type=docx",
    headers=headers,
    timeout=15
)
# 权限信息: link_share_entity(tenant_readable等), security_entity
```

### 7. 查看文档的权限成员

```python
resp = requests.get(
    f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/members?type=docx&page_size=50",
    headers=headers,
    timeout=15
)
members = resp.json()["data"]["items"]
# 每个member: {member_id(openid), member_type(openid), perm(full_access/edit/view), perm_type(container/user)}
# container = 所有者, user = 已授权用户
```

## 权限模型与作用域

### 两种 Token 的差异

| 维度 | tenant_access_token | user_access_token |
|:----|:-------------------|:-----------------|
| **身份** | 应用身份 | 用户身份 |
| **获取** | app_id + app_secret 直接请求 | OAuth 授权码流程 |
| **可读已知文档内容** | ✅ 有 drive:document 即可 | ✅ |
| **枚举应用空间** | ✅ 默认可用 | ✅ |
| **枚举用户个人空间** | ❌ | ✅ 需要 drive:drive 权限 |
| **有效期** | 2小时 | 2小时（可刷新） |

### 必需权限

| 权限 | 作用 | 何时需要 |
|:----|:-----|:---------|
| `drive:document` 或 `drive:document.readonly` | 读取文档内容 | 读任何 docx/doc 内容 |
| `drive:drive` | 列出/浏览用户云盘文件 | 枚举用户个人空间树 |
| `drive:file` | 操作文件（下载/上传） | 下载 PDF/图片文件 |

> **注意**：`tenant_access_token` + `drive:document` 只能读取已知 token 的文档，不能枚举用户个人空间。要枚举目录树，需要 `user_access_token` + `drive:drive`。

### 当前用户应用配置

- App ID: `cli_aa869b8d6b3c5cc3`
- 已启用: `drive:document`（已发布）
- 已测试: 读取 docx 内容 ✅，列出根目录文件 ✅
- 待启用: `drive:drive`（需发布新版本）+ OAuth 授权

## OAuth 授权流程（用户个人空间枚举）

### 步骤

1. **开发者后台添加权限**：应用 → 权限管理 → 添加 `drive:drive`
2. **发布新版本**：版本管理与发布 → 创建新版本
3. **用户授权**：用户在浏览器打开授权链接并确认
4. **获取 user_access_token**：通过授权码换取 token

### 授权链接格式

```
https://open.feishu.cn/open-apis/authen/v1/index?app_id={APP_ID}&redirect_uri=https%3A%2F%2Fopen.feishu.cn&scope=drive:drive,drive:document&state=1
```

### 获取 user_access_token（授权回调后）

```python
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET},
    timeout=10
)
# 注意：实际 OAuth 流程需要 authorization_code 换取 access_token
# 详见飞书 OAuth 2.0 文档
```

## Drive API 目录结构

```
应用空间 (My Space — 通过 tenant_access_token 可枚举)
├── bitables 等应用主动创建的文件
└── ...

用户个人空间 (通过 user_access_token + drive:drive 可枚举)
├── 根目录下的文件夹/文档
├── 子文件夹/文档
└── ...
```

**关键发现**：根目录 `drive/v1/files` 默认返回应用自身的 My Space。用户的个人空间需要通过 `user_access_token` 遍历。已知 token 的文档无论位置，只要在 `drive:document` 作用域内均可直接读取。

## 常见错误

| 错误码 | 含义 | 处理 |
|--------|------|------|
| 10014 | app_secret 无效 | 检查 `.env` 文件中的真实 secret（终端输出可能被截断） |
| 99992402 | 参数验证失败 | 检查请求参数名称和格式（如 `order_by` 驼峰拼写：`EditedTime` 非 `edited_time`） |
| 1063001 | 无效参数 | 文档类型不匹配，换 `doc` / `docx` / `bitable` 等重试 |
| 970005 | 文档类型不匹配 | 确认文档是 docx 还是 doc 类型（新版=docx，旧版=doc） |
| 404 | token 不存在/无权限 | 可能是 file token 已过期或被删除，或 endpoint 不存在 |
| 99991672 | 缺少contact权限 | 用户信息API需要额外的contact权限，不影响drive操作 |

## 已知API局限

- **元数据查询不返回 parent_token** — `POST /drive/v1/metas/batch_query` 对 docx 类型不返回 `parent_token` 字段，无法通过元数据确定文档在哪个文件夹。`parent_token` 仅在 `GET /drive/v1/files` 根目录列表中对 `bitable`/`file` 类型可见
- **无枚举用户个人空间的简化API** — `drive/v1/files` 仅返回应用自身空间的根目录文件。要枚举用户的个人空间目录树，必须通过 OAuth 获取 `user_access_token` + `drive:drive` 权限。不存在直接通过 `app_id + app_secret` 枚举用户空间的快捷方式
- **docx 无 `/v1/files/{token}` 详情端点** — `GET /drive/v1/files/{token}` 对 docx 文件返回 404（该端点仅支持 `file` 和 `folder` 类型）。获取 docx 元信息用 `POST /metas/batch_query`，获取内容用 `GET /docx/v1/documents/{id}/raw_content`
- **`children` 子文件夹遍历受限** — `GET /drive/v1/files/{folder_token}/children` 对 `My Space` 根文件夹（`doc_type: other`）返回 404。只有普通的 `doc_type: folder` 类型才支持列子目录

## 注意事项

- `FEISHU_APP_SECRET` 在环境变量显示 `qSk4tz...VaHN`（省略号），`.env` 文件中是完整值
- 用 `source ~/.hermes/.env` 加载真实值而非直接复制 env 输出
- tenant_access_token 有效期约 2 小时（6942秒=116分钟），每次使用前重新获取
- docx raw_content 返回纯文本，无格式信息（标题/加粗等被剥离）
- 读取/下载后的文档，按 obsidian-ingestion-pipeline 标准流程入库
- 元数据查询中的 `owner_id` 是用户的 `open_id`（`ou_xxx` 格式）
