# OpenClaw Skills

OpenClaw AI 助手技能库，提供文件自动分类等生产力工具。

## 什么是 OpenClaw？

[OpenClaw](https://github.com/openclaw/openclaw) 是一个开源的个人 AI 助手，可在任何操作系统和平台上运行。支持多种消息平台（WhatsApp、Telegram、Discord、Slack、Signal、iMessage 等）。

## 技能列表

| 技能 | 描述 | 版本 | 状态 |
|------|------|------|------|
| [file-organizer](./skills/file-organizer) | 工作区文件自动分类 - 创建即分类 | 1.0.0 | ✅ 稳定 |

## 快速开始

### 安装技能

OpenClaw 使用基于目录的技能系统。安装技能只需将技能目录复制到 OpenClaw 的技能目录：

```bash
# 克隆本仓库
git clone https://github.com/Guic3136/openclaw-skills.git

# 进入目录
cd openclaw-skills

# 复制技能到 OpenClaw 技能目录（macOS/Linux）
cp -r skills/file-organizer ~/.openclaw/skills/

# Windows (PowerShell)
Copy-Item -Recurse skills\file-organizer $env:USERPROFILE\.openclaw\skills\
```

### 验证安装

```bash
# 列出已安装的技能
openclaw skills list

# 查看技能详情
openclaw skills info file-organizer
```

## 目录结构

```
openclaw-skills/
├── skills/                        # 所有技能存放于此
│   └── file-organizer/           # 技能: 文件自动分类
│       └── SKILL.md              # 技能定义文件
├── templates/                     # 技能模板
│   └── skill-template/           # 创建新技能的模板
├── README.md                      # 项目说明
└── LICENSE                        # 许可证
```

## 技能开发指南

### 技能格式

每个 OpenClaw 技能是一个包含 `SKILL.md` 文件的目录：

```
skills/
└── my-skill/
    └── SKILL.md                  # 技能定义（必须）
```

### SKILL.md 格式

```markdown
---
name: skill-name                  # 技能标识符（必须）
description: "技能描述"          # 简短描述（必须）
homepage: https://example.com    # 可选主页
metadata:
  openclaw:
    emoji: "📁"                  # 技能图标
    requires:
      bins: ["python", "node"]   # 需要的二进制文件
---

# 技能标题

## 何时使用

✅ **使用场景：**
- 场景1
- 场景2

❌ **不使用场景：**
- 场景3

## 命令示例

```bash
# 示例命令
command --option
```

## 注意事项

- 注意事项1
- 注意事项2
```

### 创建新技能

1. 复制模板：
```bash
cp -r templates/skill-template skills/my-skill
```

2. 编辑 `SKILL.md` 文件，定义技能行为

3. 测试技能：
```bash
openclaw skills validate skills/my-skill
```

4. 提交到仓库：
```bash
git add skills/my-skill
git commit -m "Add skill: my-skill v1.0.0"
git push
```

## 与 Claude Code 技能的区别

| 特性 | OpenClaw 技能 | Claude Code 技能 |
|------|--------------|-----------------|
| 格式 | Markdown (SKILL.md) | YAML + Markdown |
| 安装 | 复制到目录 | 符号链接或复制 |
| 配置 | 元数据头部 | skill.yaml |
| 平台 | 任何支持 OpenClaw 的平台 | 仅限 Claude Code |

## 贡献

欢迎贡献新的技能！请：

1. Fork 本仓库
2. 创建你的技能分支 (`git checkout -b skill/my-skill`)
3. 提交更改 (`git commit -am 'Add skill: my-skill'`)
4. 推送到分支 (`git push origin skill/my-skill`)
5. 创建 Pull Request

## 许可证

MIT License
