---
name: file-organizer
description: "工作区文件自动分类 - 创建即分类。使用场景：新文件创建时自动分类整理、截图/脚本/配置文件归档、工作区清理。支持截图、Python脚本、Node.js脚本、配置文件等多种类型。"
homepage: https://github.com/Guic3136/openclaw-skills/tree/main/skills/file-organizer
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["python3", "mv", "mkdir"]
    tags: ["productivity", "file-management", "organization"]
---

# File Organizer - 文件自动分类技能

工作区文件自动分类 - 创建即分类，支持团队协作。

## 何时使用

✅ **使用此技能的场景：**

- 创建新文件时自动分类
- 截图/图片文件归档
- Python/Node.js 脚本整理
- 配置文件统一管理
- 工作区定期清理
- 团队协作目录标准化

❌ **不使用此技能的场景：**

- 临时文件快速查看
- 已归档文件的搜索
- 系统文件管理
- 版本控制中的文件重命名

## 核心概念

### **创建即分类**

所有文件在创建时放入正确目录，无需事后整理。

### 目录映射

| 文件类型 | 存放路径 | 说明 |
|---------|---------|------|
| 截图/图片 | `screenshots/` | PNG、JPG、GIF 等 |
| Python 脚本 | `scripts/python/` | .py 文件 |
| Node.js 脚本 | `scripts/node/` | .js、.ts 文件 |
| Shell 脚本 | `scripts/shell/` | .sh、.ps1 文件 |
| 配置文件 | `configs/` | .json、.yaml、.toml 等 |
| 报告/文档 | `output/` | .md、.pdf、.docx 等 |
| 临时文件 | `temp/` | 临时下载、缓存 |
| 工具函数 | `utils/` | 可复用的工具代码 |

## 命令示例

### 文件分类操作

```bash
# 分类单个文件到正确目录
python3 -c "
import os, shutil
file = 'image.png'
if file.endswith('.png'):
    os.makedirs('screenshots', exist_ok=True)
    shutil.move(file, f'screenshots/{file}')
    print(f'Moved {file} to screenshots/')
"

# 批量分类当前目录文件
python3 << 'EOF'
import os, shutil
from pathlib import Path

# 定义分类规则
rules = {
    'screenshots': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'],
    'scripts/python': ['.py', '.ipynb'],
    'scripts/node': ['.js', '.ts', '.jsx', '.tsx', '.mjs'],
    'scripts/shell': ['.sh', '.ps1', '.bash', '.zsh'],
    'configs': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config'],
    'output': ['.md', '.pdf', '.docx', '.txt', '.log'],
    'temp': ['.tmp', '.cache', '.bak'],
}

# 执行分类
for file in os.listdir('.'):
    if os.path.isfile(file):
        ext = Path(file).suffix.lower()
        for folder, extensions in rules.items():
            if ext in extensions:
                os.makedirs(folder, exist_ok=True)
                shutil.move(file, f'{folder}/{file}')
                print(f'✓ {file} → {folder}/')
                break
EOF
```

### 工作区初始化

```bash
# 创建标准工作区目录结构
mkdir -p {screenshots,scripts/{python,node,shell},configs,output,temp,utils}

# 创建 .gitignore 忽略临时文件
cat > .gitignore << 'EOF'
# Temporary files
temp/
*.tmp
*.cache
*.bak

# Output files (keep structure, ignore content)
output/*.pdf
output/*.docx
screenshots/*.png
!screenshots/.gitkeep

# IDE
.vscode/
.idea/
*.swp
EOF
```

### 截图自动归档

```bash
# 将桌面截图移动到截图目录
python3 << 'EOF'
import os, shutil
from pathlib import Path

desktop = Path.home() / "Desktop"
screenshot_dir = Path("screenshots")
screenshot_dir.mkdir(exist_ok=True)

# 常见截图文件名模式
patterns = ['Screen Shot', 'Screenshot', '截屏', '屏幕截图', 'image']

for file in desktop.iterdir():
    if file.is_file():
        if any(pattern in file.name for pattern in patterns):
            dest = screenshot_dir / file.name
            shutil.move(str(file), str(dest))
            print(f"✓ Moved: {file.name} → screenshots/")
EOF
```

### Python 脚本管理

```bash
# 创建新的 Python 脚本并放入正确目录
python3 << 'EOF'
import os
from datetime import datetime

script_name = input("Enter script name (without .py): ")
script_dir = "scripts/python"
os.makedirs(script_dir, exist_ok=True)

script_content = f'''#!/usr/bin/env python3
"""
{script_name}.py
Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Description: 
"""

def main():
    pass

if __name__ == "__main__":
    main()
'''

file_path = f"{script_dir}/{script_name}.py"
with open(file_path, 'w') as f:
    f.write(script_content)

os.chmod(file_path, 0o755)
print(f"✓ Created: {file_path}")
EOF
```

### 配置管理

```bash
# 创建并管理配置文件
python3 << 'EOF'
import os
import json

config_dir = "configs"
os.makedirs(config_dir, exist_ok=True)

# 创建应用配置
app_config = {
    "app_name": "my-app",
    "version": "1.0.0",
    "settings": {
        "debug": False,
        "log_level": "info"
    }
}

config_path = f"{config_dir}/app.json"
with open(config_path, 'w') as f:
    json.dump(app_config, f, indent=2)

print(f"✓ Config saved: {config_path}")
EOF
```

## 高级用法

### 自定义分类规则

```python
# custom_rules.py
import os
import shutil
from pathlib import Path

# 自定义分类规则
CUSTOM_RULES = {
    # 项目特定目录
    'frontend': ['.tsx', '.jsx', '.css', '.scss', '.vue'],
    'backend': ['.go', '.rs', '.java', '.php', '.rb'],
    'data': ['.csv', '.json', '.parquet', '.db', '.sqlite'],
    'docs': ['.md', '.rst', '.adoc'],
    'assets': ['.png', '.jpg', '.gif', '.ico', '.woff', '.ttf'],
}

def organize_by_custom_rules(directory='.'):
    """使用自定义规则分类文件"""
    for file in os.listdir(directory):
        file_path = Path(directory) / file
        if file_path.is_file():
            ext = file_path.suffix.lower()
            for folder, extensions in CUSTOM_RULES.items():
                if ext in extensions:
                    target_dir = Path(directory) / folder
                    target_dir.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(target_dir / file))
                    print(f"✓ {file} → {folder}/")
                    break

if __name__ == "__main__":
    organize_by_custom_rules()
```

### 文件去重

```bash
# 检测并删除重复文件
python3 << 'EOF'
import os
import hashlib
from collections import defaultdict

def file_hash(filepath):
    """计算文件 MD5 哈希"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(directory='.'):
    """查找重复文件"""
    hashes = defaultdict(list)
    
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                file_hash_val = file_hash(filepath)
                hashes[file_hash_val].append(filepath)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    
    # 显示重复文件
    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    for file_hash_val, paths in duplicates.items():
        print(f"\nDuplicate files (hash: {file_hash_val[:8]}...):")
        for path in paths:
            print(f"  - {path}")
    
    return duplicates

# 执行查找
find_duplicates()
EOF
```

### 自动清理临时文件

```bash
# 清理超过 7 天的临时文件
python3 << 'EOF'
import os
import time
from datetime import datetime, timedelta

temp_dir = "temp"
if not os.path.exists(temp_dir):
    print("Temp directory does not exist")
    exit()

cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days ago
deleted_count = 0

for filename in os.listdir(temp_dir):
    filepath = os.path.join(temp_dir, filename)
    if os.path.isfile(filepath):
        file_time = os.path.getmtime(filepath)
        if file_time < cutoff_time:
            os.remove(filepath)
            deleted_count += 1
            print(f"Deleted: {filename}")

print(f"\nTotal deleted: {deleted_count} files")
EOF
```

## 团队协作

### 标准化目录结构

```bash
# setup-workspace.sh - 团队工作区初始化脚本
#!/bin/bash

echo "Setting up standardized workspace..."

# 创建目录结构
mkdir -p {screenshots,scripts/{python,node,shell},configs,output,temp,utils}

# 创建 README
cat > README.md << 'EOF'
# Workspace

## Directory Structure

- `screenshots/` - Screenshots and images
- `scripts/` - Executable scripts
  - `python/` - Python scripts
  - `node/` - Node.js scripts
  - `shell/` - Shell scripts
- `configs/` - Configuration files
- `output/` - Generated reports and documents
- `temp/` - Temporary files (auto-cleaned)
- `utils/` - Utility functions and helpers

## Usage

New files are automatically organized to appropriate directories.
EOF

# 创建 .gitkeep 保持空目录结构
for dir in screenshots scripts/python scripts/node scripts/shell configs output temp utils; do
    touch "$dir/.gitkeep"
done

echo "✓ Workspace setup complete!"
```

### Git 集成

```bash
# 在 .gitattributes 中管理文件分类
# 参考: https://git-scm.com/docs/gitattributes

cat >> .gitattributes << 'EOF'
# Mark generated files
output/** linguist-generated=true
screenshots/** linguist-generated=true
temp/** linguist-generated=true

# Treat configs as documentation
configs/*.md linguist-documentation
EOF
```

## 注意事项

- **备份重要文件**：在执行批量移动操作前确认文件已备份
- **检查文件名冲突**：移动前确认目标目录没有同名文件
- **临时文件自动清理**：`temp/` 目录的文件可能会被自动清理
- **配置文件版本控制**：`configs/` 中的敏感配置应加入 `.gitignore`
- **截图隐私**：`screenshots/` 中可能包含敏感信息，分享前注意脱敏

## 故障排除

### 权限问题

```bash
# 修复权限
chmod -R u+w scripts/ configs/ output/
```

### 路径问题

```bash
# 使用绝对路径
python3 -c "import os; print(os.path.abspath('.'))"
```

### 移动失败

```bash
# 检查文件是否被占用
lsof +D .
```
