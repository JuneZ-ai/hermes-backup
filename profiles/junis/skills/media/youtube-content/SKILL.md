---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
# Core dependency for transcript fetching
pip install youtube-transcript-api

# Optional: for metadata (title/author/date) and cover image download
pip install yt-dlp
```

### Proxy Configuration (WSL / Restricted Networks)

When running inside WSL behind a Windows proxy (e.g. BitZ/Clash/v2rayN):

1. **On Windows**: Enable "Allow LAN" in your proxy software settings so WSL can reach it.
2. **From WSL**: Set proxy env vars using the Windows host IP (not 127.0.0.1):

```bash
WIN_IP=$(ip route | grep default | awk '{print $3}')
export HTTP_PROXY="http://${WIN_IP}:7897"
export HTTPS_PROXY="http://${WIN_IP}:7897"
export ALL_PROXY="socks5://${WIN_IP}:7897"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
export all_proxy="$ALL_PROXY"
```

Common proxy ports by software: BitZ(7897), Clash(7890), v2rayN HTTP(10809), Shadowsocks(1080).

**Testing proxy reachability:**
```bash
curl -sx "http://${WIN_IP}:7897" --connect-timeout 5 --max-time 10 \
  "https://www.youtube.com/oembed?url=https://youtube.com/watch?v=dQw4w9WgXcQ&format=json"
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps
- **Obsidian note**: Standard `.md` file ready to drag into Obsidian vault (see below)

### Example — Obsidian Note

```markdown
---
title: "视频标题"
author: "频道名"
source: "https://youtube.com/watch?v=VIDEO_ID"
date: 2026-05-26
tags: [youtube, video, 笔记]
cover: "assets/VIDEO_ID.jpg"
duration: "12:34"
status: done
---

# 视频标题

> 摘要：2-3句话视频概述

![[VIDEO_ID.jpg]]

## 元信息
- **频道**: 频道名
- **发布日期**: 2026-05-26
- **时长**: 12:34
- **链接**: [YouTube](https://youtube.com/watch?v=VIDEO_ID)

## 完整字幕

00:00 开场介绍
01:23 第一主题
...
```

Cover image saved as `assets/VIDEO_ID.jpg` relative to the note, or in a vault-level `assets/` folder.

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
