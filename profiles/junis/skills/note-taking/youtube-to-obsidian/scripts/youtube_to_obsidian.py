#!/usr/bin/env python3
"""
YouTube → Obsidian .md 转换器 v2 (whisper 后备)

用法：
    python3 youtube_to_obsidian.py "视频URL" [--output ./output_dir]

依赖：
    pip install yt-dlp faster-whisper

特点：
    - 自动识别来源：YouTube 走代理，优酷/B站直连
    - 有字幕 → 直接抓取（完美）
    - 无字幕 → 自动下载音频 + Whisper 语音转写（15-30分钟/小时视频）
    - 输出带 frontmatter + 封面 + 完整对话的 Obsidian .md
"""

import argparse
import os
import re
import subprocess
import sys
import json
import time

# === 代理配置 ===
PROXY = "socks5://172.24.0.1:7897"

# === 自定义包路径（faster-whisper 装在 ~/.local/lib 下） ===
_WHISPER_PATH = os.path.expanduser("~/.local/lib/hermes-whisper")
if os.path.isdir(_WHISPER_PATH):
    sys.path.insert(0, _WHISPER_PATH)

# === 视频来源判断 ===
YOUKU_DOMAINS = ["youku.com", "youku.", "ykimg.com"]
BILI_DOMAINS = ["bilibili.com", "b23.tv"]
DIRECT_DOMAINS = YOUKU_DOMAINS + BILI_DOMAINS


def is_direct_site(url: str) -> bool:
    """国内视频站，直连不需要代理"""
    url_lower = url.lower()
    for d in DIRECT_DOMAINS:
        if d in url_lower:
            return True
    return False


def get_proxy_args(url: str) -> list:
    """根据来源决定代理参数"""
    if is_direct_site(url):
        return ["--proxy", ""]  # Youku/B站直连
    return ["--proxy", PROXY]   # YouTube 走代理


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|youtu\.be/|shorts/|embed/|live/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return url


def sanitize_filename(s: str, max_len: int = 60) -> str:
    s = re.sub(r'[\\/:*?"<>|]', '_', s)
    s = s.strip().replace(' ', '_')
    if len(s) > max_len:
        s = s[:max_len]
    return s


def run_cmd(cmd: list, timeout: int = 120, env: dict = None) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    if result.returncode != 0:
        err = result.stderr[:300]
        raise RuntimeError(f"命令失败: {err}")
    return result.stdout.strip()


# ── 1. 元信息 ──────────────────────────────────────────

def fetch_metadata(video_url: str) -> dict:
    """获取视频元信息"""
    fields = ["title", "uploader", "upload_date", "duration", "thumbnail", "webpage_url"]
    proxy_args = get_proxy_args(video_url)
    vid = extract_video_id(video_url)

    # 优先走 yt-dlp
    try:
        flat_cmd = ["yt-dlp"] + proxy_args
        for f in fields:
            flat_cmd.extend(["--print", f])
        flat_cmd.append(video_url)

        stdout = run_cmd(flat_cmd, timeout=60)
        lines = [l.strip() for l in stdout.split('\n') if l.strip()]

        if len(lines) >= 6:
            title = lines[0]
            uploader = lines[1].replace("Get APP now", "").replace("-Get APP now", "").strip()
            return {
                "title": title,
                "uploader": uploader,
                "upload_date": lines[2],
                "duration": int(lines[3]) if lines[3].isdigit() else 0,
                "thumbnail": lines[4],
                "webpage_url": lines[5],
                "video_id": vid,
                "source_site": "youku" if is_direct_site(video_url) else "youtube",
            }
    except Exception as e:
        print(f"  ⚠ yt-dlp 元信息失败: {e}", file=sys.stderr)

    # 保底方案
    return {
        "title": f"Video ({vid})",
        "uploader": "Unknown",
        "upload_date": "",
        "duration": 0,
        "thumbnail": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
        "webpage_url": video_url,
        "video_id": vid,
        "source_site": "unknown",
    }


# ── 2. 封面下载 ────────────────────────────────────────

def download_cover(meta: dict, output_dir: str, url: str) -> str:
    """下载视频封面"""
    thumb_url = meta.get("thumbnail", "")
    if not thumb_url:
        vid = meta["video_id"]
        thumb_url = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"

    filename = f"{sanitize_filename(meta['title'])}_cover.jpg"
    filepath = os.path.join(output_dir, filename)

    # 优酷的封面走直连
    if is_direct_site(url):
        cmd = ["curl", "-sL", "--connect-timeout", "10", "--max-time", "20",
               "-o", filepath, thumb_url]
    else:
        proxy_http = PROXY.replace("socks5://", "socks5h://")
        cmd = ["curl", "-sL", "-x", proxy_http,
               "--connect-timeout", "10", "--max-time", "20",
               "-o", filepath, thumb_url]

    try:
        subprocess.run(cmd, capture_output=True, timeout=30, check=True)
        if os.path.getsize(filepath) > 1000:
            return filename
    except Exception as e:
        print(f"  ⚠ 封面下载失败: {e}", file=sys.stderr)
    return ""


# ── 3. 字幕获取 ────────────────────────────────────────

def fetch_subtitles(video_id: str, output_dir: str, url: str) -> list:
    """用 yt-dlp 下载字幕"""
    proxy_args = get_proxy_args(url)
    out_template = os.path.join(output_dir, f"sub_{video_id}")
    cmd = [
        "yt-dlp"] + proxy_args + [
        "--write-auto-subs", "--sub-langs", "zh-Hans,zh,en",
        "--skip-download", "--sub-format", "vtt",
        "-o", out_template,
        url,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return []
    except:
        return []

    for ext in [".zh-Hans.vtt", ".zh.vtt", ".en.vtt",
                 ".zh-Hans-CN.vtt", ".zh-CN.vtt"]:
        fpath = out_template + ext
        if os.path.exists(fpath):
            with open(fpath, encoding='utf-8') as f:
                segments = parse_vtt(f.read())
            os.remove(fpath)
            return segments

    return []


def parse_vtt(vtt_text: str) -> list:
    """解析 VTT 字幕"""
    segments = []
    lines = vtt_text.strip().split('\n')
    i = 0
    while i < len(lines):
        m = re.match(r'(\d{1,2}:\d{2}:\d{2}\.\d{3})\s+-->\s+', lines[i])
        if m:
            start_ts = m.group(1)
            i += 1
            text_parts = []
            while i < len(lines):
                line = lines[i].strip()
                if not line or re.match(r'\d{1,2}:\d{2}:', line):
                    break
                if not line.startswith('<'):
                    text_parts.append(line)
                i += 1
            if text_parts:
                segments.append({
                    "start": ts_to_sec(start_ts),
                    "text": ' '.join(text_parts).replace('\n', ' '),
                })
        else:
            i += 1
    return segments


def ts_to_sec(ts: str) -> float:
    parts = ts.replace(',', '.').split(':')
    if len(parts) == 3:
        return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0])*60 + float(parts[1])
    return 0


# ── 4. Whisper 语音转写（后备） ────────────────────────

def download_audio(video_url: str, output_dir: str, video_id: str) -> str:
    """用 yt-dlp 下载音频"""
    proxy_args = get_proxy_args(video_url)
    audio_path = os.path.join(output_dir, f"{video_id}.mp3")
    cmd = [
        "yt-dlp"] + proxy_args + [
        "--extract-audio", "--audio-format", "mp3",
        "--audio-quality", "10",
        "-o", audio_path,
        video_url,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        for f in os.listdir(output_dir):
            if f.startswith(video_id) and f.endswith(".mp3"):
                return os.path.join(output_dir, f)
    except subprocess.TimeoutExpired:
        print("  ⏰ 音频下载超时", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠ 音频下载失败: {e}", file=sys.stderr)
    return ""


def transcribe_audio(audio_path: str) -> list:
    """用 faster-whisper 转写音频"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  ⚠ faster-whisper 未安装，跳过语音转写", file=sys.stderr)
        print("  💡 安装: pip install faster-whisper", file=sys.stderr)
        return []

    print(f"\n  🎤 开始语音转写（较大模型需下载，首次约 2-5分钟）...", file=sys.stderr)
    sys.stderr.flush()

    start = time.time()
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, language="zh", beam_size=5)

    result = []
    for seg in segments:
        result.append({
            "start": seg.start,
            "text": seg.text.strip(),
        })

    elapsed = time.time() - start
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    print(f"  ✅ 转写完成 ({mins}分{secs}秒, {len(result)}段)", file=sys.stderr)

    return result


# ── 5. 生成 Markdown ──────────────────────────────────

def fmt_ts(seconds: float) -> str:
    if seconds >= 3600:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}:{m:02d}:{s:02d}"
    total = int(seconds)
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return ""
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def generate_markdown(meta: dict, segments: list, cover_file: str, source_type: str) -> str:
    title = meta["title"]
    author = meta["uploader"]
    date_raw = meta.get("upload_date", "")
    date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}" if date_raw else ""
    dur = format_duration(meta["duration"])
    url = meta["webpage_url"]

    lines = []
    lines.append("---")
    lines.append(f'title: "{title}"')
    lines.append(f'author: "{author}"')
    if date_fmt:
        lines.append(f"date: {date_fmt}")
    lines.append(f'source: "{url}"')
    lines.append(f"tags: [{source_type}, video]")
    if cover_file:
        lines.append(f'cover: "{cover_file}"')
    if dur:
        lines.append(f'duration: "{dur}"')
    lines.append("status: watched")
    lines.append("rating: ")
    lines.append("---\n")
    lines.append(f"# {title}\n")

    if cover_file:
        lines.append(f"![[{cover_file}]]\n")

    lines.append(">")
    if author:
        lines.append(f"> **作者：** {author}")
    if date_fmt:
        lines.append(f"> **发布日期：** {date_fmt}")
    lines.append(f"> **链接：** [{url}]({url})")
    if dur:
        lines.append(f"> **时长：** {dur}")
    lines.append("")

    # 对话内容标题
    if segments:
        lines.append("## 🎙 对话\n")
        total_seg = len(segments)
        # 如果段落太多（>200），分段合并
        if total_seg > 200:
            # 合并成句子段落（每7-15秒一组）
            merged = []
            buffer = ""
            buf_start = 0
            for seg in segments:
                if not buffer:
                    buffer = seg["text"]
                    buf_start = seg["start"]
                else:
                    # 如果超过 12 秒或句子完结
                    if seg["start"] - buf_start > 12 or seg["text"].endswith(("。", "？", "！", ".", "?", "!")):
                        merged.append({"start": buf_start, "text": buffer})
                        buffer = seg["text"]
                        buf_start = seg["start"]
                    else:
                        buffer += " " + seg["text"]
            if buffer:
                merged.append({"start": buf_start, "text": buffer})

            for seg in merged:
                lines.append(f"- **{fmt_ts(seg['start'])}** {seg['text']}")
        else:
            for seg in segments:
                lines.append(f"- **{fmt_ts(seg['start'])}** {seg['text']}")
    else:
        lines.append("*（无字幕且语音转写不可用）*\n")

    lines.append("\n---\n## 💡 笔记\n")

    return '\n'.join(lines)


# ── 6. 主流程 ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="视频 → Obsidian .md")
    parser.add_argument("url", help="视频 URL（YouTube / 优酷 / B站）")
    parser.add_argument("--output", "-o", default=".", help="输出目录")
    parser.add_argument("--no-whisper", action="store_true", help="禁用语音转写后备")
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    vid = extract_video_id(args.url)
    site = "优酷" if is_direct_site(args.url) else "YouTube"
    print(f"🎬 来源: {site}  |  ID: {vid}")

    # 1. 元信息
    print("📥 获取元信息...", end=" ", flush=True)
    meta = fetch_metadata(args.url)
    print(f"✅ [{meta['uploader']}] {meta['title'][:50]}")

    # 2. 封面
    print("🖼 下载封面...", end=" ", flush=True)
    cover = download_cover(meta, output_dir, args.url)
    print(f"{'✅' if cover else '⚠ 跳过'}")

    # 3. 字幕（优先）
    print("📝 获取字幕...", end=" ", flush=True)
    segs = fetch_subtitles(meta["video_id"], output_dir, args.url)
    source_type = "youtube"

    if segs:
        print(f"✅ 字幕 {len(segs)} 条")
    elif args.no_whisper:
        print("⚠ 无字幕（已禁用语音转写）")
    else:
        print("⚠ 无字幕 → 启动语音转写后备")
        source_type = site.lower()

        # 3a. 下载音频
        print("  📥 下载音频...", end=" ", flush=True)
        audio_path = download_audio(args.url, output_dir, meta["video_id"])
        if audio_path:
            print(f"✅ ({os.path.getsize(audio_path)//1024//1024}MB)")
            # 3b. Whisper 转写
            segs = transcribe_audio(audio_path)
            # 清理音频文件
            try:
                os.remove(audio_path)
            except:
                pass
        else:
            print("❌ 音频下载失败")

    # 4. 生成 Markdown
    print("📄 生成 Markdown...", end=" ", flush=True)
    md = generate_markdown(meta, segs, cover, source_type)
    safe_title = sanitize_filename(meta["title"])
    safe_author = sanitize_filename(meta["uploader"])
    fname = f"{safe_author}_{safe_title}.md"
    fpath = os.path.join(output_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(md)
    print("✅")

    print(f"\n📄 {fpath}")
    if cover:
        print(f"🖼 {cover}")
    print(f"🎙 对话: {len(segs)} 条")
    print("拖入 Obsidian 即可使用")


if __name__ == "__main__":
    main()
