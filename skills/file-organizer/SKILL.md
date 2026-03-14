---
name: file-organizer
description: "文件自动分类 - 支持单项目(类型优先)和多项目(项目优先)两种模式。使用场景：工作区文件整理、多项目管理、截图/脚本/配置文件归档。"
homepage: https://github.com/Guic3136/openclaw-skills/tree/main/skills/file-organizer
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["python3", "mv", "mkdir"]
    tags: ["productivity", "file-management", "organization", "project-management"]
---

# File Organizer - 文件自动分类技能

智能文件分类系统，支持**单项目**和**多项目**两种组织模式。

## 何时使用

✅ **使用此技能的场景：**

- 创建新文件时自动分类
- 同时管理多个项目的文件
- 项目之间文件隔离与组织
- 截图/图片文件归档
- Python/Node.js 脚本整理
- 工作区定期清理

❌ **不使用此技能的场景：**

- 系统文件管理
- 版本控制中的文件重命名
- 临时文件快速查看

## 核心概念

### 两种组织模式

#### 模式一：类型优先（适合单项目）

所有文件按**类型**分类，适合单个项目的工作区：

```
workspace/
├── screenshots/          # 所有截图
├── scripts/
│   ├── python/          # Python 脚本
│   ├── node/            # Node.js 脚本
│   └── shell/           # Shell 脚本
├── configs/             # 配置文件
├── output/              # 报告和文档
├── temp/                # 临时文件
└── utils/               # 工具函数
```

#### 模式二：项目优先（适合多项目）

文件先按**项目**分类，再按类型分类，适合同时开发多个项目：

```
projects/
├── ProjectA/
│   ├── screenshots/
│   ├── scripts/
│   ├── configs/
│   └── output/
├── ProjectB/
│   ├── screenshots/
│   ├── scripts/
│   ├── configs/
│   └── output/
└── shared/              # 跨项目共享文件
    ├── scripts/
    └── configs/
```

### 智能项目检测

自动检测当前目录是否为项目根目录：

| 检测标志 | 说明 |
|---------|------|
| `.git/` | Git 仓库根目录 |
| `package.json` | Node.js 项目 |
| `requirements.txt` / `pyproject.toml` | Python 项目 |
| `README.md` | 项目说明文件 |
| `src/` 或 `source/` | 源代码目录 |

## 命令示例

### 模式切换与配置

```bash
# 设置组织模式为"项目优先"
export FILE_ORGANIZER_MODE=project

# 设置项目根目录（默认当前目录）
export FILE_ORGANIZER_ROOT=~/projects

# 设置类型优先模式的目录结构
export FILE_ORGANIZER_TYPE_DIRS="screenshots,scripts/python,scripts/node,configs,output,temp"
```

### 项目优先模式 - 初始化项目结构

```bash
# 创建新项目并初始化目录结构
python3 << 'EOF'
import os
from pathlib import Path

project_name = input("Enter project name: ")
base_dir = Path(os.environ.get("FILE_ORGANIZER_ROOT", "~/projects")).expanduser()
project_dir = base_dir / project_name

# 创建项目目录结构
dirs = [
    "screenshots",
    "scripts/python",
    "scripts/node",
    "scripts/shell",
    "configs",
    "output",
    "temp",
    "docs",
    "assets"
]

for d in dirs:
    (project_dir / d).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {project_name}/{d}/")

# 创建项目 README
readme_content = f"""# {project_name}

## Directory Structure

- `screenshots/` - Screenshots and images
- `scripts/` - Executable scripts (python, node, shell)
- `configs/` - Configuration files
- `output/` - Generated reports and documents
- `temp/` - Temporary files (auto-cleaned)
- `docs/` - Documentation
- `assets/` - Project assets

## Auto-Organization

Files are automatically organized based on type and extension.
"""

(project_dir / "README.md").write_text(readme_content)
print(f"\n✓ Project '{project_name}' initialized at {project_dir}")
EOF
```

### 项目优先模式 - 文件分类

```bash
# 将文件分类到指定项目
python3 << 'EOF'
import os
import shutil
from pathlib import Path

# 配置
base_dir = Path(os.environ.get("FILE_ORGANIZER_ROOT", "~/projects")).expanduser()
project_name = input("Enter target project name: ")
project_dir = base_dir / project_name

if not project_dir.exists():
    print(f"Error: Project '{project_name}' not found at {project_dir}")
    exit(1)

# 分类规则（与类型优先模式相同，但目标在项目目录内）
rules = {
    'screenshots': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'],
    'scripts/python': ['.py', '.ipynb'],
    'scripts/node': ['.js', '.ts', '.jsx', '.tsx', '.mjs'],
    'scripts/shell': ['.sh', '.ps1', '.bash', '.zsh'],
    'configs': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf'],
    'output': ['.md', '.pdf', '.docx', '.txt', '.log'],
    'assets': ['.ico', '.woff', '.ttf', '.eot'],
    'temp': ['.tmp', '.cache', '.bak'],
}

# 分类当前目录的文件
for file in os.listdir('.'):
    if os.path.isfile(file):
        ext = Path(file).suffix.lower()
        for folder, extensions in rules.items():
            if ext in extensions:
                target_dir = project_dir / folder
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(file, target_dir / file)
                print(f"✓ {file} → {project_name}/{folder}/")
                break

print(f"\n✓ Files organized to project '{project_name}'")
EOF
```

### 自动检测项目并分类

```bash
# 智能分类 - 根据当前目录自动判断项目
python3 << 'EOF'
import os
import shutil
from pathlib import Path

def find_project_root(path='.'):
    """向上查找项目根目录（包含 .git 的目录）"""
    current = Path(path).resolve()
    while current != current.parent:
        if (current / '.git').exists() or \
           (current / 'package.json').exists() or \
           (current / 'requirements.txt').exists() or \
           (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    return None

def organize_file(file_path, project_root=None):
    """将文件分类到正确位置"""
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    rules = {
        'screenshots': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'],
        'scripts/python': ['.py', '.ipynb'],
        'scripts/node': ['.js', '.ts', '.jsx', '.tsx', '.mjs'],
        'scripts/shell': ['.sh', '.ps1', '.bash', '.zsh'],
        'configs': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf'],
        'output': ['.md', '.pdf', '.docx', '.txt', '.log'],
        'temp': ['.tmp', '.cache', '.bak'],
    }

    # 确定目标目录
    if project_root:
        base_dir = project_root
        print(f"Detected project: {project_root.name}")
    else:
        base_dir = Path('.')
        print("No project detected, using current directory")

    # 执行分类
    for folder, extensions in rules.items():
        if ext in extensions:
            target_dir = base_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_dir / file_path.name))
            print(f"✓ {file_path.name} → {target_dir.relative_to('.')}/")
            return True

    print(f"✗ No rule for: {file_path.name}")
    return False

# 使用示例
file_to_organize = input("Enter file path (or '.' for all files): ")

if file_to_organize == '.':
    # 分类当前目录所有文件
    project_root = find_project_root()
    for f in os.listdir('.'):
        if os.path.isfile(f):
            organize_file(f, project_root)
else:
    # 分类单个文件
    project_root = find_project_root(os.path.dirname(file_to_organize) or '.')
    organize_file(file_to_organize, project_root)
EOF
```

### 跨项目文件移动

```bash
# 将文件从一个项目移动到另一个项目
python3 << 'EOF'
import os
import shutil
from pathlib import Path

base_dir = Path(os.environ.get("FILE_ORGANIZER_ROOT", "~/projects")).expanduser()

# 列出所有项目
print("Available projects:")
for i, proj in enumerate(base_dir.iterdir(), 1):
    if proj.is_dir():
        print(f"  {i}. {proj.name}")

source_project = input("\nSource project: ")
target_project = input("Target project: ")
filename = input("File to move: ")

source = base_dir / source_project / filename
target = base_dir / target_project / filename

if source.exists():
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    print(f"✓ Moved: {source_project}/{filename} → {target_project}/{filename}")
else:
    print(f"✗ File not found: {source}")
EOF
```

### 项目间文件去重

```bash
# 在所有项目中查找重复文件
python3 << 'EOF'
import os
import hashlib
from pathlib import Path
from collections import defaultdict

def file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

base_dir = Path(os.environ.get("FILE_ORGANIZER_ROOT", "~/projects")).expanduser()

# 收集所有文件的哈希
hashes = defaultdict(list)

for project_dir in base_dir.iterdir():
    if project_dir.is_dir():
        for root, _, files in os.walk(project_dir):
            for filename in files:
                filepath = Path(root) / filename
                try:
                    h = file_hash(filepath)
                    hashes[h].append((project_dir.name, filepath.relative_to(project_dir)))
                except:
                    pass

# 显示跨项目重复
print("Cross-project duplicates:")
for h, locations in hashes.items():
    if len(locations) > 1:
        projects = set(loc[0] for loc in locations)
        if len(projects) > 1:  # 只在不同项目间重复
            print(f"\nHash: {h[:8]}...")
            for proj, path in locations:
                print(f"  - [{proj}] {path}")
EOF
```

## 注意事项

- **项目隔离**：确保不同项目的文件不会混淆
- **默认项目**：无法确定项目时，使用 `misc` 或 `inbox` 作为临时存放
- **跨项目共享**：公共资源放在 `shared/` 或专门的共享项目
- **备份策略**：多项目模式下，建议按项目分别备份
- **命名规范**：项目名称使用小写字母和连字符，避免空格

## 故障排除

### 项目检测失败

```bash
# 手动指定项目
export FILE_ORGANIZER_PROJECT=my-project
organize file.txt
```

### 权限问题

```bash
# 修复项目目录权限
chmod -R u+w ~/projects/
```

### 文件冲突

```bash
# 重命名冲突文件
mv file.txt "file_$(date +%Y%m%d_%H%M%S).txt"
```
