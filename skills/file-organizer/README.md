# File Organizer - OpenClaw Skill

📁 智能文件自动分类与目录管理技能

## 简介

File Organizer 是一个为 OpenClaw 设计的混合模式文件管理技能，能够在用户显式请求时提供建议，在 OpenClaw 自动创建文件时执行自动分类。

## 功能特点

### 🎯 双模式运行

- **建议模式**: 用户主动询问时提供分类建议，等待确认后执行
- **自动模式**: OpenClaw 自动生成文件时自动分类，无需确认

### 🔍 智能检测

- **项目类型检测**: 支持 13 种项目类型（Python、Node.js、React、Vue、Go、Rust、Java 等）
- **外部项目警告**: 检测到 .git、LICENSE、README 等标志时发出警告
- **内容分析**: 根据文件内容推断类型（如 React 组件、Python Web 等）

### 📂 智能分类

- 12 种预设文件类型规则（截图、脚本、配置、数据等）
- 自动子目录选择（如 data/raw、data/processed、data/external）
- 智能命名建议（时间戳、序号、哈希）

### 🛡️ 安全机制

- 冲突检测与自动解决
- 完整操作记录与回滚支持
- 外部项目保护（防止破坏已有结构）

## 安装

将本技能复制到 OpenClaw 技能目录：

```bash
cp -r skills/file-organizer ~/.openclaw/skills/
```

或者通过 Git 克隆整个仓库：

```bash
git clone https://github.com/Guic3136/openclaw-skills.git
cd openclaw-skills
```

## 使用方法

### 1. 用户显式触发（建议模式）

当用户询问文件存放位置或要求整理工作区时触发：

```
用户: "我新建了一个 config.yaml，应该放哪里？"
用户: "帮我整理一下这个工作区"
用户: "我要创建一个新项目"
```

**响应示例**:

```
📋 文件分类建议
━━━━━━━━━━━━━━━━━━━
📄 文件: config.yaml
📁 建议位置: configs/

💡 理由: 配置文件统一放在 configs/ 便于管理

📋 操作选项:
[1] ✅ 接受 - 移动到 configs/config.yaml
[2] ✏️  修改 - 告诉我您的偏好
[3] ❌ 取消 - 保持当前位置
```

### 2. OpenClaw 自动触发（自动模式）

当 OpenClaw 自动生成文件时自动分类：

```
📁 自动分类
━━━━━━━━━━━━━━━━━━━
✓ script.py → scripts/python/data_processor.py
  规则: python_scripts
  置信度: 0.92

[已自动执行，无需确认]
```

### 3. 外部项目检测（警告模式）

当检测到外部引入的完整项目时：

```
⚠️  检测到外部项目结构
━━━━━━━━━━━━━━━━━━━
发现以下项目标志:
   - .git/ (Git仓库)
   - package.json (Node.js项目)
   - README.md (项目说明)

这是一个可能来自外部的完整项目，具有自己的目录结构。

请选择:
[1] 🏠 保持原样（推荐）- 不修改目录结构
[2] 📝 仅对新文件应用 - 现有文件保持不动
[3] ⚠️  全面重组（有风险）- 创建完整备份后执行
```

## 配置

### 运行模式

编辑 `hooks/openclaw/hook.yaml` 中的 `global_config.mode`：

```yaml
global_config:
  mode: balanced  # conservative | balanced | aggressive
```

- **conservative**: 所有操作都询问确认
- **balanced**: 自动分类新建文件，移动现有文件时询问（默认）
- **aggressive**: 最大程度自动执行

### 自定义规则

编辑 `rules/default-rules.json` 添加自定义分类规则：

```json
{
  "rules": [
    {
      "id": "my_custom_rule",
      "name": "自定义规则",
      "extensions": [".myext"],
      "directory": "custom/",
      "confidence": 0.9
    }
  ]
}
```

### 本地覆盖

在项目根目录创建 `.claude/organization-rules.local.json` 覆盖全局规则：

```json
{
  "team_settings": {
    "allow_local_override": true
  },
  "rules": [
    // 本地自定义规则
  ]
}
```

## 项目结构

```
skills/file-organizer/
├── SKILL.md                      # 技能定义文件
├── README.md                     # 本文件
├── hooks/
│   └── openclaw/
│       └── hook.yaml            # 钩子配置
├── rules/
│   └── default-rules.json       # 默认分类规则
└── scripts/
    ├── auto-classifier.py       # 自动分类器
    ├── project-detector.py      # 项目类型检测器
    └── conflict-resolver.py     # 冲突解决器
```

## 脚本工具

### auto-classifier.py

自动分类决策器，用于确定文件的最佳存放位置：

```bash
# 分析文件分类
python3 scripts/auto-classifier.py myfile.py

# 指定项目目录和运行模式
python3 scripts/auto-classifier.py config.json --project-dir /path/to/project --mode balanced

# 使用内容分析
python3 scripts/auto-classifier.py app.py --content "import React from 'react'"
```

### project-detector.py

检测项目类型和结构：

```bash
# 检测当前目录项目类型
python3 scripts/project-detector.py

# 检测指定目录
python3 scripts/project-detector.py --path /path/to/project

# JSON 格式输出
python3 scripts/project-detector.py --output json
```

### conflict-resolver.py

处理文件移动冲突：

```bash
# 检测冲突并建议解决方案
python3 scripts/conflict-resolver.py ./source.py ./target.py

# 使用指定策略解决
python3 scripts/conflict-resolver.py ./source.py ./target.py --strategy timestamp

# 执行移动并记录
python3 scripts/conflict-resolver.py ./source.py ./target.py --execute --action MOVE

# 生成回滚脚本
python3 scripts/conflict-resolver.py --generate-rollback-only
```

## 分类规则

| 规则ID | 文件类型 | 目标目录 | 子目录 |
|--------|----------|----------|--------|
| screenshots | 图片文件 (.png, .jpg, etc.) | screenshots/ | web, design, docs |
| python_scripts | Python脚本 (.py, .ipynb) | scripts/python/ | utils, analysis, automation |
| node_scripts | Node.js脚本 (.js, .ts) | scripts/node/ | utils, build, deploy |
| shell_scripts | Shell脚本 (.sh, .ps1) | scripts/shell/ | - |
| configs | 配置文件 (.json, .yaml) | configs/ | - |
| output_docs | 输出文档 (.md, .pdf) | output/ | reports, exports, generated |
| data_files | 数据文件 (.csv, .xlsx) | data/ | raw, processed, external, archive |
| temp_files | 临时文件 (.log, .tmp) | temp/ | - |
| utils | 工具函数 | utils/ | - |
| docs | 项目文档 (.md) | docs/ | - |
| tests | 测试文件 | tests/ | unit, integration, e2e |
| assets | 静态资源 (.css, .woff) | assets/ | fonts, styles, icons |

## 日志与回滚

所有操作自动记录到 `~/.openclaw/skills/file-organizer/logs/`：

```bash
# 查看操作日志
ls -la ~/.openclaw/skills/file-organizer/logs/

# 查看具体操作
cat ~/.openclaw/skills/file-organizer/logs/operations_YYYYMMDD.jsonl

# 执行回滚
bash ~/.openclaw/skills/file-organizer/logs/rollback_YYYYMMDD_HHMMSS.sh
```

## 注意事项

1. **外部项目保护**: 当检测到 .git、LICENSE 等标志时，会提示用户确认，防止破坏现有项目结构
2. **自动备份**: 全面重组前建议手动备份或选择创建备份
3. **团队协作**: 共享规则可以通过 Git 仓库同步（配置 `team_settings`）

## 开发计划

- [x] 基础自动分类功能
- [x] 项目类型检测
- [x] 冲突解决与回滚
- [ ] 可视化配置界面
- [ ] 规则性能评估
- [ ] 更多项目类型支持

## 许可证

MIT License - 详见根目录 LICENSE 文件

## 作者

Leo Baher - OpenClaw 技能开发

---

**提示**: 本技能是 OpenClaw 的文件管理辅助工具，最终决策权始终在用户手中。
