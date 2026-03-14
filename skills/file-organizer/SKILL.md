---
name: file-organizer
description: "文件自动分类。Use when: (1) 用户创建新项目，(2) 用户询问文件放哪里，(3) 用户主动要求整理工作区，(4) OpenClaw 自动生成/下载文件时，(5) 检测到外部引入的完整项目。主要用途：目录结构设计、文件自动分类、工作区整理。"
homepage: https://github.com/Guic3136/openclaw-skills/tree/main/skills/file-organizer
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["python3", "mv", "mkdir"]
    tags: ["productivity", "file-management", "organization", "project-management"]
    hooks:
      config: hooks/openclaw/hook.yaml
      triggers:
        - user_explicit_create
        - agent_auto_create
        - before_file_write
        - external_project_detect
---

# File Organizer - 文件自动分类技能

为**新建项目**和**新建文件**提供目录结构设计建议和自动分类。

## 运行模式

本技能支持两种运行模式，根据触发场景自动选择：

### 模式1：建议模式（用户显式触发）

**触发条件：**
- 用户说"我要创建一个新项目"
- 用户问"这个文件应该放哪里"
- 用户说"帮我整理工作区"

**行为特征：**
- 分析文件类型和项目结构
- 提供详细的分类建议
- **等待用户确认后再执行**
- 显示理由和备选方案

### 模式2：自动分类模式（OpenClaw 自动触发）

**触发条件：**
- OpenClaw 自动生成代码文件
- OpenClaw 下载并保存资源
- OpenClaw 写入配置文件
- OpenClaw 生成输出文档

**行为特征：**
- 自动识别文件类型
- 直接选择最佳目录
- **自动执行，无需询问**
- 执行后通知用户结果

### 模式配置

通过配置控制自动分类的激进程度：

```yaml
# ~/.openclaw/config/file-organizer.yaml
mode: balanced  # conservative | balanced | aggressive

conservative:  # 保守模式
  auto_classify: false
  confirm_before_move: true

balanced:      # 平衡模式（默认）
  auto_classify: true
  confirm_before_move: true
  confidence_threshold: 0.7

aggressive:    # 积极模式
  auto_classify: true
  confirm_before_move: false
  confidence_threshold: 0.5
```

## Quick Reference

| 场景 | 触发信号 | 模式 | 处理方式 |
|------|---------|------|---------|
| 创建新项目 | "开始新项目" / "create project" | 建议模式 | 推荐目录结构 → 询问确认 |
| 询问文件位置 | "放哪里" / "where to save" | 建议模式 | 分析类型 → 建议位置 → 等待确认 |
| 整理工作区 | "整理" / "organize" | 建议模式 | 预览 → 确认 → 执行 → 记录 |
| OpenClaw 生成文件 | `agent_file_create` 事件 | 自动模式 | 识别类型 → 直接分类 → 通知 |
| OpenClaw 下载文件 | `agent_download_save` 事件 | 自动模式 | 按类型放入对应目录 |
| 外部项目检测 | 发现 .git/package.json 等 | 警告模式 | 警告 → 询问 → 可选保持原样 |

## 响应格式标准

根据运行模式，使用不同的输出格式：

### 格式A：建议模式（用户显式触发）

用于：用户询问"放哪里"、"怎么组织"

```
📋 文件分类建议
━━━━━━━━━━━━━━━━━━━
📄 文件: script.py
📁 建议位置: scripts/python/
📝 命名: data_processor.py

💡 理由: Python脚本按功能分类到 scripts/python/ 便于管理
       符合 organization-rules.json 中的 python_scripts 规则

📋 操作选项:
[1] ✅ 接受 - 创建到 scripts/python/data_processor.py
[2] ✏️  修改 - 告诉我您的偏好
[3] ❌ 取消 - 保持当前位置
```

### 格式B：自动分类模式（OpenClaw 自动触发）

用于：OpenClaw 自主创建文件

```
📁 自动分类
━━━━━━━━━━━━━━━━━━━
✓ script.py → scripts/python/data_processor.py
  规则: python_scripts
  置信度: 0.92
  时间: 2026-03-14 14:30:15

[已自动执行，无需确认]
```

### 格式C：批量自动分类

用于：一次创建多个文件

```
📦 批量自动分类（5个文件）
━━━━━━━━━━━━━━━━━━━
✓ script.py         → scripts/python/    (置信度: 0.92)
✓ config.json       → configs/           (置信度: 0.88)
✓ screenshot.png    → screenshots/       (置信度: 0.95)
✓ data.csv          → data/raw/          (置信度: 0.85)
⚠️  unknown.xyz      → misc/              (类型未知)

[全部自动执行完成]
点击展开查看详细信息...
```

### 格式D：警告模式（外部项目）

用于：检测到外部引入的完整项目

```
⚠️  检测到外部项目结构
━━━━━━━━━━━━━━━━━━━
发现以下项目标志:
   - .git/ (Git仓库)
   - package.json (Node.js项目)
   - README.md (项目说明)

这是一个可能来自外部的完整项目，具有自己的目录结构。
自动重组可能破坏现有结构。

请选择:
[1] 🏠 保持原样（推荐）- 不修改目录结构，仅对新文件分类
[2] 📝 仅对新文件应用 - 现有文件保持不动
[3] ⚠️  全面重组（有风险）- 创建完整备份后执行重组
```

### 格式E：操作日志

用于：记录每次分类操作

```
📄 操作记录
━━━━━━━━━━━━━━━━━━━
ID: ORG-20260314-001
时间: 2026-03-14 14:30:15
操作: MOVE
源路径: ./script.py
目标路径: ./scripts/python/data_processor.py
规则: python_scripts
模式: 自动分类
置信度: 0.92
状态: 已完成

回滚命令:
  mv ./scripts/python/data_processor.py ./script.py
```

## ⚠️ 重要提示（给 OpenClaw AI 助手）

### 使用范围

本技能主要用于以下场景：
- ✅ **用户要创建新项目** - 提供推荐的目录结构设计
- ✅ **用户新建单个/少量文件** - 建议放置位置
- ✅ **用户主动要求整理工作区** - 执行分类操作

**以下场景需要特别注意：**

### 🚨 处理外部项目时的警告流程

当用户通过以下方式引入外部项目时：
- `git clone` 克隆的仓库
- 下载并解压的压缩包
- 从其他位置复制/移动过来的完整项目
- 第三方提供的项目文件

**必须执行以下步骤：**

1. **暂停并提醒用户**
   ```
   ⚠️ 检测到这是一个完整的外部项目，具有自己的目录结构。

   当前项目结构：
   - src/ (源代码)
   - tests/ (测试文件)
   - docs/ (文档)
   - README.md

   是否要重新组织这个项目的目录结构？

   [注意] 重新组织可能会：
   - 破坏项目的相对路径引用
   - 影响构建脚本和工具配置
   - 导致版本控制混乱

   请选择：
   1. 保持原样（推荐）
   2. 仅对新文件使用此结构
   3. 全面重组（有风险，需备份）
   ```

2. **如果用户选择重组，必须：**
   - 创建完整的操作日志（用于回滚）
   - 预览即将执行的所有操作
   - 确认用户明确同意

3. **执行前创建回滚记录**
   ```bash
   # 记录当前文件位置
   find . -type f > ~/.file-organizer/backup/$(date +%Y%m%d_%H%M%S)_before_organize.txt
   ```

### 📝 操作记录要求

**所有文件移动操作必须记录：**

```bash
# 标准日志格式
# 时间戳 | 操作类型 | 源路径 | 目标路径 | 文件哈希

# 示例
2026-03-14_14:30:15 | MOVE | ./script.py | ./scripts/python/script.py | a1b2c3d4
2026-03-14_14:30:16 | MOVE | ./config.json | ./configs/config.json | e5f6g7h8
```

**回滚脚本生成：**

每次整理完成后，自动生成回滚脚本：

```bash
# 生成回滚命令
echo "#!/bin/bash" > ~/.file-organizer/rollback/rollback_20260314_143015.sh
echo "# 回滚脚本 - 生成时间: 2026-03-14 14:30:15" >> ~/.file-organizer/rollback/rollback_20260314_143015.sh
echo "mv ./scripts/python/script.py ./script.py" >> ~/.file-organizer/rollback/rollback_20260314_143015.sh
chmod +x ~/.file-organizer/rollback/rollback_20260314_143015.sh
```

## 何时使用

✅ **推荐使用：**

- **创建全新项目** - "我要开始一个新项目，帮我设计目录结构"
- **新建零散文件** - "我新建了几个脚本文件，应该放哪里"
- **主动整理请求** - "帮我整理一下这个工作区"
- **规划项目结构** - "给这个项目推荐一个目录组织方式"

❌ **不推荐/需谨慎：**

- **已有完整结构的项目** - 如通过 git clone 获得的项目
- **团队协作项目** - 除非所有成员同意
- **生产环境代码** - 避免影响运行中的系统

## 核心概念

### 本技能的设计原则

**"新建即正确"** - 在创建时就提供建议，而不是事后整理。

#### 对比说明

| 场景 | 本技能处理方式 | 示例 |
|------|--------------|------|
| 用户说"我要创建一个新项目" | ✅ 主动推荐目录结构 | "建议创建以下目录：scripts/, configs/, ..." |
| 用户说"这个文件放哪" | ✅ 给出具体放置建议 | "这是一个Python脚本，建议放到 scripts/python/" |
| 用户说"帮我整理这个目录" | ⚠️ 先询问、记录、再执行 | 生成预览 → 确认 → 执行 → 提供回滚 |
| 检测到完整的外部项目 | ❌ 警告并询问 | "这是一个已有结构的项目，是否保持原样？" |

### 两种组织模式

#### 模式一：类型优先（适合新建单项目）

所有文件按**类型**分类：

```
my-new-project/          <- 用户创建的新项目
├── screenshots/         # 截图和图片
├── scripts/
│   ├── python/         # Python 脚本
│   ├── node/           # Node.js 脚本
│   └── shell/          # Shell 脚本
├── configs/            # 配置文件
├── output/             # 输出文档
├── temp/               # 临时文件
└── docs/               # 项目文档
```

#### 模式二：项目优先（适合管理多个新建项目）

文件先按**项目**分类：

```
projects/
├── NewProjectA/        <- 用户创建的新项目A
│   ├── screenshots/
│   ├── scripts/
│   ├── configs/
│   └── output/
├── NewProjectB/        <- 用户创建的新项目B
│   ├── screenshots/
│   ├── scripts/
│   ├── configs/
│   └── output/
└── shared/             # 共享资源
```

## 命令示例

### 场景1：用户要创建新项目

```python
# 推荐对话流程：
# 用户："我要开始一个新的数据分析项目"
# OpenClaw："好的，建议为您的数据分析项目创建以下目录结构："

python3 << 'EOF'
import os
from pathlib import Path

project_name = "data-analysis-project"  # 用户提供
base_dir = Path.home() / "projects" / project_name

# 推荐的数据分析项目结构
dirs = [
    "data/raw",           # 原始数据
    "data/processed",     # 处理后数据
    "notebooks",          # Jupyter notebooks
    "scripts/python",     # Python 处理脚本
    "scripts/sql",        # SQL 查询
    "configs",            # 配置文件
    "output/reports",     # 分析报告
    "output/visualizations",  # 可视化图表
    "docs",               # 文档
]

print(f"📁 建议的目录结构：{project_name}/")
for d in dirs:
    print(f"   ├── {d}/")

response = input("\n是否创建这个目录结构？(y/n): ")
if response.lower() == 'y':
    for d in dirs:
        (base_dir / d).mkdir(parents=True, exist_ok=True)
    print(f"\n✓ 已创建项目：{base_dir}")
EOF
```

### 场景2：用户新建文件询问位置

```python
# 推荐对话流程：
# 用户："我新建了一个 config.yaml，应该放哪里？"
# OpenClaw："根据文件类型，建议放置位置如下："

filename = "config.yaml"  # 用户提供

# 自动识别文件类型并给出建议
file_type_map = {
    '.yaml': ('configs/', '配置文件'),
    '.json': ('configs/', '配置文件'),
    '.py': ('scripts/python/', 'Python脚本'),
    '.js': ('scripts/node/', 'Node.js脚本'),
    '.sh': ('scripts/shell/', 'Shell脚本'),
    '.png': ('screenshots/', '图片文件'),
    '.md': ('docs/', '文档'),
}

ext = filename.split('.')[-1] if '.' in filename else ''
if f'.{ext}' in file_type_map:
    folder, desc = file_type_map[f'.{ext}']
    print(f"📄 {filename} ({desc})")
    print(f"   建议位置: {folder}{filename}")
    print(f"   理由: 这是{desc}，统一放在{folder}便于管理")
else:
    print(f"未识别的文件类型，建议询问用户")
```

### 场景3：用户主动要求整理（带完整记录）

```bash
# 完整流程：询问 → 预览 → 确认 → 执行 → 记录 → 提供回滚

python3 << 'EOF'
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# 步骤1：询问确认
print("⚠️  您确定要整理当前目录吗？")
print("这将移动文件到新的位置。")
response = input("继续？(yes/no/preview): ")

if response == 'preview':
    preview_only = True
elif response == 'yes':
    preview_only = False
else:
    print("已取消")
    exit()

# 步骤2：生成操作日志ID
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path.home() / '.file-organizer' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"organize_{timestamp}.json"

# 步骤3：分析并预览
operations = []
rules = {
    'screenshots': ['.png', '.jpg', '.jpeg', '.gif'],
    'scripts/python': ['.py', '.ipynb'],
    'scripts/node': ['.js', '.ts'],
    'configs': ['.json', '.yaml', '.yml'],
    'docs': ['.md', '.txt'],
}

for file in os.listdir('.'):
    if os.path.isfile(file):
        ext = Path(file).suffix.lower()
        for folder, extensions in rules.items():
            if ext in extensions:
                operations.append({
                    'action': 'MOVE',
                    'source': f'./{file}',
                    'target': f'./{folder}/{file}',
                    'timestamp': timestamp
                })
                break

# 步骤4：显示预览
print(f"\n📋 即将执行的操作（共{len(operations)}个）：")
for op in operations:
    print(f"   {op['source']} → {op['target']}")

if preview_only:
    print("\n[预览模式，未执行任何操作]")
    exit()

# 步骤5：再次确认
confirm = input("\n确认执行？(输入 'organize' 确认): ")
if confirm != 'organize':
    print("已取消")
    exit()

# 步骤6：执行并记录
for op in operations:
    src = Path(op['source'])
    tgt = Path(op['target'])
    tgt.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(tgt))
    print(f"✓ {op['source']} → {op['target']}")

# 步骤7：保存日志
with open(log_file, 'w') as f:
    json.dump(operations, f, indent=2)

# 步骤8：生成回滚脚本
rollback_script = log_dir / f"rollback_{timestamp}.sh"
with open(rollback_script, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write(f"# 回滚脚本 - 生成时间: {timestamp}\n")
    f.write(f"# 日志文件: {log_file}\n\n")
    for op in reversed(operations):  # 逆序回滚
        f.write(f'mv "{op["target"]}" "{op["source"]}"\n')
    f.write('\necho "✓ 回滚完成"\n')
os.chmod(rollback_script, 0o755)

print(f"\n✅ 整理完成！")
print(f"📄 操作日志: {log_file}")
print(f"↩️  回滚脚本: {rollback_script}")
print(f"\n如需回滚，运行: bash {rollback_script}")
EOF
```

### 场景4：检测到外部项目时的处理

```python
# 当检测到可能的外部项目时，必须执行的检查流程

python3 << 'EOF'
import os
from pathlib import Path

# 检测外部项目的标志
EXTERNAL_PROJECT_INDICATORS = [
    '.git',              # Git仓库
    'package.json',      # Node.js项目
    'requirements.txt',  # Python项目
    'Cargo.toml',        # Rust项目
    'go.mod',            # Go项目
    'pom.xml',           # Maven项目
    'build.gradle',      # Gradle项目
    'Makefile',
    'CMakeLists.txt',
]

def check_external_project(path='.'):
    """检查是否为外部引入的完整项目"""
    indicators_found = []
    for indicator in EXTERNAL_PROJECT_INDICATORS:
        if (Path(path) / indicator).exists():
            indicators_found.append(indicator)
    return indicators_found

# 执行检查
indicators = check_external_project()

if indicators:
    print("🚨 检测到外部项目标志：")
    for ind in indicators:
        print(f"   - {ind}")

    print("\n⚠️  警告：这是一个可能来自外部的完整项目，具有自己的目录结构。")
    print("\n选项：")
    print("1. 保持原样（推荐）- 不修改目录结构")
    print("2. 仅对新文件应用建议结构")
    print("3. 全面重组 - 需要创建完整备份")

    choice = input("\n请选择 (1/2/3): ")

    if choice == '1':
        print("✓ 保持项目原样。如需新建文件，我将单独建议存放位置。")
    elif choice == '2':
        print("✓ 仅对新文件应用分类。现有文件保持不动。")
    elif choice == '3':
        print("⚠️  您选择了全面重组。正在创建完整备份...")
        # 创建备份...
    else:
        print("默认保持原样。")
else:
    print("✓ 未检测到外部项目标志，可以安全地提供目录建议。")
EOF
```

## 团队协作最佳实践

### 项目模板创建

```bash
# 为新项目创建标准模板
mkdir -p ~/templates/standard-project
cd ~/templates/standard-project

mkdir -p {screenshots,scripts/{python,node,shell},configs,output,temp,docs}

cat > README.md << 'EOF'
# {{PROJECT_NAME}}

## 目录结构说明

本项目使用 file-organizer 推荐的目录结构：

- `screenshots/` - 截图和图片文件
- `scripts/` - 可执行脚本
- `configs/` - 配置文件
- `output/` - 输出文档和报告
- `temp/` - 临时文件（可自动清理）
- `docs/` - 项目文档

## 文件存放指南

新建文件时，根据文件类型放入对应目录。
EOF
```

## 注意事项

- **本技能是辅助工具** - 提供建议，最终决策权在用户
- **优先保护现有结构** - 对外来项目保持谨慎
- **记录一切变更** - 确保可以回滚
- **明确沟通** - 让用户清楚知道将要发生什么

## 故障排除

### 回滚操作

```bash
# 如果整理后出现问题，执行回滚
bash ~/.file-organizer/logs/rollback_YYYYMMDD_HHMMSS.sh
```

### 查看历史操作

```bash
# 列出所有整理记录
ls -la ~/.file-organizer/logs/

# 查看具体操作
cat ~/.file-organizer/logs/organize_YYYYMMDD_HHMMSS.json
```
