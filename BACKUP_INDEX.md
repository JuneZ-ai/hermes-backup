---
title: Hermes 迁移备份索引
updated: 2026-07-20
---

# 🗄️ Hermes 迁移备份索引

## 备份策略

- **位置**: `D:\hermes-backups\`（本地 D 盘）
- **GitHub**: 仅存此索引文件，原始备份在本地
- **保留**: 最近 4 份，自动轮转
- **用途**: 换设备时下载此包即可完整迁移
- **备份范围**: 配置 / SOUL / 自定义skills / 脚本 / 记忆系统 / cron / SSH

## 备份清单

| # | 文件名 | 大小 | 创建时间 | MD5
|:-:|:------|:---:|:--------:|:----
| 1 | `hermes-migration-2026-07-20.tar.gz` | 527MB | 2026-07-20 10:01 | `85104aee4cfde759...` |
| 2 | `hermes-migration-2026-07-13.tar.gz` | 479MB | 2026-07-13 10:37 | `3bb3eb9241bcf0fb...` |

**总计: 2 份备份, 0.98GB**

## 迁移指引

1. 新机器安装 Hermes
2. 从 `D:\hermes-backups\` 复制最新 `.tar.gz` 到新机器
3. 解压覆盖 `~/.hermes/` 和 `~/.ssh/`
4. 重启 Hermes → 一切恢复

> ⚠️ 解压前备份新机器上已有的 `~/.hermes/config.yaml`，确认 API Key 配置正确。
