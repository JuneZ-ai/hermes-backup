# 飞书云盘文件下载 → OB 入库

> 适用于 `my.feishu.cn/file/<token>` 类型的文件（非 docx/sheet/bitable，而是普通文件型附件，如读书笔记文档）。

---

## 一、前置条件

- `lark-cli` 已安装并配置（Windows npm: `C:\Users\18502\AppData\Roaming\npm\lark-cli`）
- 已用 `lark-cli config init` 配置了飞书 app_id/app_secret/brand=feishu
- 飞书应用具有 `drive:drive` 相关权限

## 二、获取文件列表

```bash
# 列出云盘根文件
lark-cli drive files list --params '{"page_size":30}' --page-all --format json

# 检查某个文件夹内的文件
lark-cli drive files list --params '{"page_size":30,"parent_token":"<folder_token>"}' --format json
```

## 三、下载文件

lark-cli 的 `+download` 命令**要求相对路径作为输出**，必须先 cd 到目标目录：

```bash
cd /path/to/download/dir

lark-cli drive +download \
  --file-token "<file_token>" \
  --output "./filename"
```

**file_token 提取：** 从 `my.feishu.cn/file/ZLVFbKyLcoo0dCxS8hhc1FsmnBf` 中的 `/file/` 后取到文件尾。

## 四、识别文件类型

下载后使用 `file` 命令识别类型：

```bash
file /path/to/file
# 输出示例: "Unicode text, UTF-8 text" 或 "PDF document" 等
```

## 五、分类入库规则

飞书云盘中的读书笔记，根据内容分类：

| 内容类型 | 目标目录 | 示例 |
|---------|---------|------|
| 哲学/思维方法论 | 六韬道史/ | 《第一性原理》李善友 |
| 个人成长/策略 | 六韬智脑/ | 《格局逆袭》宗宁 |
| 文史哲经典 | 六韬易哲/文史哲/ | 文学/历史类书籍 |

## 六、完整流程

1. 「lark-cli drive files list」查看云盘文件
2. 识别需要下载的笔记 → 提取 file_token
3. `cd` 到 tmp 目录 → `lark-cli drive +download` 下载
4. `read_file` 读取内容
5. 按分类写入 OB vault 对应目录
6. 更新搭建日志 + WB 协作接口
7. 清理 tmp 文件
