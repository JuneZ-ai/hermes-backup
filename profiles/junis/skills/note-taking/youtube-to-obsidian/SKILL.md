---
name: youtube-to-obsidian
description: |
  YouTube 视频 → Obsidian 标准 .md 文件。
  自动抓取视频标题、作者、发布日期、封面图、完整字幕，
  打包成带 frontmatter 的 Obsidian 笔记，直接拖进库就能用。
  触发词：「扒视频」「转视频」「视频→笔记」「油管转Obsidian」「抓字幕」
platforms: [linux, macos, windows]
requires:
  - yt-dlp
  - youtube-transcript-api
proxy:
  default: socks5://172.24.0.1:7897
---

# YouTube → Obsidian 转换器

## 用法

```
python3 SKILL_DIR/scripts/youtube_to_obsidian.py "YouTube_URL" [--output OUTPUT_DIR]
```

示例：
```bash
python3 ~/.hermes/skills/note-taking/youtube-to-obsidian/scripts/youtube_to_obsidian.py "https://www.youtube.com/watch?v=qvY0-PslC-E"
```

输出：在当前目录生成一个 `.md` 文件，文件名格式 `{作者}_{标题}.md`

## 输出格式

生成的 `.md` 文件包含：

```yaml
---
title: "视频标题"
author: "频道名"
date: 2025-12-01
source: "https://youtube.com/watch?v=..."
tags: [youtube, video]
cover: "{{title}}.jpg"
duration: "1:23:45"
status: watched
rating: 
---

# 视频标题

![[{{title}}.jpg]]

> 作者：频道名
> 发布日期：2025-12-01
> 链接：[YouTube](https://youtube.com/watch?v=...)

## 字幕

00:00 第一句字幕
00:05 第二句字幕
...
```

## 依赖安装

```bash
pip install yt-dlp youtube-transcript-api
```

## 代理配置

默认代理：script 中内置 socks5://172.24.0.1:7897
如需修改，编辑脚本顶部 PROXY 变量。
