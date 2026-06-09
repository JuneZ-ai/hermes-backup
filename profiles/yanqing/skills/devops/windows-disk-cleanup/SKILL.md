---
name: windows-disk-cleanup
description: Inspect and clean Windows C drive junk/trash from WSL. Check disk usage, locate temp files/browser caches/recycle bin, categorize by safety, and clean.
category: devops
---

# Windows Disk Cleanup (from WSL)

Trigger: User asks about cleaning their Windows C drive, disk space, junk files, temp files.

## Workflow

### 1. Overview — Check Total Usage

```bash
df -h /mnt/c
```

Note the total/used/available and percentage. If under 10% free, mention urgency.

### 2. Scan Known Junk Locations

Use a combined script with timeouts — WSL scanning Windows FS is slow. Batch key paths together:

**Safe to clean (high confidence):**
- `Users/<username>/AppData/Local/Temp` — user temp
- `Users/<username>/AppData/Local/Google/Chrome/User Data/Default/Cache` — Chrome cache
- `Users/<username>/AppData/Local/Microsoft/Edge/User Data/Default/Cache` — Edge cache
- `Users/<username>/AppData/Local/Microsoft/Windows/INetCache` — IE/Edge legacy cache
- `Users/<username>/.cache` — user cache
- `Windows/Temp` — system temp (may have in-use files)
- `ProgramData/Package Cache` — installer cache (may need admin to delete)

**Needs user confirmation:**
- `Users/<username>/Downloads` — downloaded files
- `Users/<username>/Desktop` — desktop files (often large)
- `$Recycle.Bin` — recycle bin
- `Users/<username>/AppData/Roaming/Tencent` — WeChat/QQ data (big but contains chat history)
- `Users/<username>/Documents/WeChat Files` — WeChat received files
- `Windows/Installer` — MSI cache (do NOT touch unless user explicitly says)

Use `du -sh --apparent-size <path>` with `timeout 15` per path to avoid hangs.

### 3. Categorize Results

Present results in three tiers:

```
✅ 安全可清理 — direct rm -rf, no user impact
⚠️ 需确认 — ask user before deleting
🚫 不建议动 — system-critical
```

### 4. Clean Safe Items

Parallel rm commands for speed:

```bash
rm -rf /mnt/c/Users/<username>/AppData/Local/Temp/*
rm -rf /mnt/c/Users/<username>/AppData/Local/Google/Chrome/User\ Data/Default/Cache/*
rm -rf /mnt/c/Users/<username>/AppData/Local/Microsoft/Edge/User\ Data/Default/Cache/*
rm -rf /mnt/c/Users/<username>/.cache/*
rm -rf /mnt/c/Users/<username>/AppData/Local/Microsoft/Windows/INetCache/*
rm -rf "/mnt/c/ProgramData/Package Cache/*"
```

Note: Files in use will remain — that's normal. Report residual size.

### 5. Report Results

Show a before → after comparison table. Re-run `df -h /mnt/c` to show overall freed space.

## Pitfalls

- **Windows FS is slow from WSL** — always use `timeout N` on `du` commands. If `du` times out, note it and move on rather than retrying.
- **Some paths have spaces** — quote paths or escape spaces (`Tencent/WeChat` not `Tencent\ WeChat`).
- **`$Recycle.Bin` is per-drive** — it's at `/mnt/c/\$Recycle.Bin`, not under Users.
- **ProgramData/Package Cache** often requires Windows admin rights to delete from WSL — `rm` may succeed (exit 0) but no space is freed. Check with `du` afterward.
- **WeChat stores data in 3+ locations** — check `Documents/WeChat Files`, `AppData/Roaming/Tencent/xwechat`, `AppData/Roaming/Tencent/WeChat`. The biggest is usually `xwechat` (~5G).
- **WeChat's built-in cleanup** is safer than direct deletion (preserves chat records). The user should do it manually via: Settings → General → Storage Space Management.
- **Desktop files can be 10-20G+** — flag it, but don't touch it without user instruction.
- **Downloads folder is often 5-10G** — list top 10 largest items for user to evaluate.

## References

See `references/common-junk-paths.md` for the canonical path list with descriptions.
