# 飞书大文档操作技巧

当文档含大量 block（22篇以上文章 > 300 block）时，`lark-cli docs +fetch` 默认整篇读取容易超时被系统 kill。

## 常用绕过手法

| 场景 | 手法 | 说明 |
|:----|:----|:------|
| 只看结构 | `--scope outline --detail with-ids` | 最轻量，秒回 |
| 找特定 block | `--scope keyword --keyword "关键词" --detail with-ids` | 精准定位 |
| 定位后修改 | keyword 查出 block_id → `block_replace` / `block_insert_after` | 两步走 |
| 全文超时 | `timeout 12` + `head -20` 管道，或分 `--scope section` 多次拉 | 分片突破 |

## 典型场景：在超时大文档中改一个字

```bash
# 1. keyword 定位找 block_id
timeout 12 lark-cli docs +fetch --api-version v2 --doc TOKEN --scope keyword --keyword "目标词" --detail with-ids 2>/dev/null | head -20

# 2. 拿到 block_id 后 block_replace
lark-cli docs +update --api-version v2 --doc TOKEN --command block_replace --block-id "doxcntKa..." --content '<h3>修正后内容</h3>'
```

## 原则

一旦文档大到整篇 fetch 超时，**切换到分片策略**。`--scope keyword` 是最精准的入口。
