# Hermes Backup — 六韬AI团队全栈恢复指南

## 备份内容

```
hermes-backup/
├── profiles/
│   ├── junis/          # 调度中枢（我）
│   │   ├── config.yaml # 配置 + API凭证
│   │   ├── skills/     # 19个自定义技能
│   │   └── cron/       # 定时任务
│   ├── yanqing/        # 执行管家
│   ├── huanglaoxie/    # 分析师
│   ├── luban/          # 内容工匠
│   └── saodiseng/      # 扫地僧
├── state.db            # 记忆 + 会话历史
└── README.md           # 本文件
```

## 恢复步骤

### 前置条件
1. Windows 11 + WSL2 + Ubuntu 24.04+
2. Hermes Agent 已安装（`npm install -g hermes-agent`）
3. Node.js 20+

### 第一步：还原配置
```bash
# 解压到 WSL
tar xzf ~/Desktop/hermes-backup.tar.gz -C /tmp/
# 覆盖 profiles
cp -r /tmp/hermes-backup/profiles/* /home/hermes/.hermes/profiles/
# 还原记忆
cp /tmp/hermes-backup/state.db /home/hermes/.hermes/profiles/junis/state.db
```

### 第二步：还原 API 凭证
备份中的 config.yaml 已脱敏（API Key 被替换为 `...`）。恢复后需要重新填入：
- DeepSeek API Key（config.yaml → providers → openrouter → api_key）
- NVIDIA NIM API Key（同上 custom provider）
- lark-cli 认证：`lark-cli auth login`

### 第三步：还原 Obsidian 知识库
C 盘挂了的话，知识库需从云端（OneDrive/手动备份）恢复：
`C:\Users\18502\Documents\Obsidian Vault\`

### 第四步：验证启动
```bash
hermes start
# 检查所有bot是否在线
hermes status
```

## 首次备份后自动更新
备份已复制到 Windows 桌面：`C:\Users\18502\Desktop\hermes-backup.tar.gz`

建议将此仓库设为 `hermes-backup` 私有仓库，以后每两周手动拉一次最新备份推上去。

## 注意事项
- config.yaml 中的 API Key 是脱敏的，恢复后需手动填入
- state.db 包含所有记忆和对话历史，是 bot 人格的基础
- 每个 bot 的 skills/ 目录独立，恢复后各 bot 技能完整
