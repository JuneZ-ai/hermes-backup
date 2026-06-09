# 飞书读书笔记创作（lark-cli docs v2）

> Absorbed from `lark-doc-reading-note` (2026-05-31 consolidation). Complementary to the archive workflow in the main knowledge-architecture SKILL.md: create the Feishu doc reading note first, then archive it to the Obsidian vault.

## 标准结构（三层）

### 第一层：基本信息

紧接文档导言之后，用 `<h2>📖 基本信息</h2>` + 结构化 `<p>` 列表：

```xml
<h2>📖 基本信息</h2>
<p><b>书名：</b>...</p>
<p><b>作者：</b>...</p>
<p><b>出版：</b>...</p>
<p><b>卷册：</b>...</p>
<p><b>精读篇数：</b>...</p>
<p><b>时间跨度：</b>...</p>
<p><b>一句话定位：</b>...</p>
<hr/>
```

### 第二层：核心框架表

```xml
<h2>🔑 核心框架：XXX</h2>
<table>
<colgroup><col width="120"/><col width="200"/><col/></colgroup>
<thead><tr><th>支柱</th><th>核心内涵</th><th>代表性篇目</th></tr></thead>
<tbody>
<tr><td><b>XXX</b></td><td>...</td><td>...</td></tr>
</tbody>
</table>
<hr/>
```

### 第三层：正文（每篇四维结构）

写作背景 / 核心论点(含原文引用`<blockquote>`) / 方法论价值(`<ul>`) / 金句摘录(`<ol>`)：

```xml
<h2>一、文章标题（年份）</h2>
<callout emoji="⭐" background-color="light-yellow" border-color="yellow"><p>金句</p></callout>
<hr/>
<h3>写作背景</h3><p>...</p>
<h3>核心论点</h3><blockquote><p>原文</p></blockquote><p>...</p>
<h3>方法论价值</h3><ul><li>...</li></ul>
<h3>金句摘录</h3><ol><li>...</li></ol>
```

## 创作工作流

### Phase 1: 骨架创建（串行）

1. 整理好本地 md 笔记
2. `lark-cli docs +create --api-version v2` 骨架（标题+导言callout+基本信息+核心框架表+所有章节标题+占位摘要）
3. ⚠️ 不要一次性塞完整正文到 `--content`，超长会触发字符限制

### Phase 2: 正文填充（可并行）

1. `--scope outline --detail with-ids` 获取所有 block ID
2. 对每篇文章目标位置执行 `block_insert_after`
3. 可启动 delegate_task 子代理并行填充不同卷

### Phase 3: 同时期作品插入

在相关文章之后按时间线插入诗词/信件等：
1. 找到目标文章的「金句摘录」h3 block_id
2. `block_insert_after` 插入 `<callout emoji="📜">同时期诗词</callout>`
3. ⚠️ 历史时间线必须准确，不清楚的不要插入

### Phase 4: 结尾章节

填充核心概念体系表、附录一览表、精选金句合集等收尾章节

### Phase 5: 归档到知识库（见主 SKILL.md 的 Step 4）

## 大文档处理（必读陷阱）

当文档超过约200个block后，`docs +fetch --detail with-ids` 必定超时。

### 获取 block ID 的三个方法

**方法一：`--scope outline`** — 返回所有 h1-h3 的 block_id
```bash
lark-cli docs +fetch --api-version v2 --doc "TOKEN" --scope outline --detail with-ids
```

**方法二：`--scope keyword`** — 关键词精准定位
```bash
lark-cli docs +fetch --api-version v2 --doc "TOKEN" --scope keyword --keyword "关键词"
```

**方法三：组合使用** — 先 keyword 定位 → 再对目标 block 执行操作

### ⚠️ block_insert_after 链式操作陷阱

多次对**同一个 anchor block** 执行 `block_insert_after` 会产生后进先出顺序：

```bash
# ❌ 错误
第一次：block_insert_after anchor_A → 插入到 anchor 后
第二次：block_insert_after anchor_A → 插入到 anchor 与第一次内容之间！

# ✅ 正确：每次使用上一次插入的最后一个 block
```

**稳妥方案**：将所有内容整合到单次 `block_insert_after` 调用。

### block_replace 精准修复

```bash
lark-cli docs +update --api-version v2 --doc "TOKEN" \
  --command block_replace \
  --block-id "doxcnt..." \
  --content '<h3>修正后的标题</h3>'
```

## 权威来源优先级

**当用户提供源文件/链接时，以用户提供的为准，不依赖训练记忆。**
- 不确定的创作时间/来源/内容，标注为「存疑」或暂不插入

## 工作量参考

- 骨架创建：~1分钟
- 每篇文章填充：~30秒
- 22篇精读+诗词插入：总计约3-5分钟
