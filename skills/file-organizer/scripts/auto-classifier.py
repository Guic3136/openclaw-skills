#!/usr/bin/env python3
"""
自动分类决策器 - OpenClaw File Organizer Skill

用于 OpenClaw 自动创建文件时决定文件放置位置。
支持：
1. 文件类型识别（基于扩展名和内容）
2. 项目类型检测
3. 置信度计算
4. 自动执行决策

Author: Leo Baher
Version: 1.0.0
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 默认规则（当配置文件不存在时使用）
DEFAULT_RULES = {
    "version": "1.0.0",
    "rules": [
        {
            "id": "screenshots",
            "name": "截图文件",
            "extensions": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"],
            "directory": "screenshots",
            "confidence": 0.95
        },
        {
            "id": "python_scripts",
            "name": "Python脚本",
            "extensions": [".py", ".ipynb", ".pyw"],
            "directory": "scripts/python",
            "confidence": 0.9
        },
        {
            "id": "node_scripts",
            "name": "Node.js脚本",
            "extensions": [".js", ".ts", ".mjs", ".cjs"],
            "directory": "scripts/node",
            "confidence": 0.9
        },
        {
            "id": "shell_scripts",
            "name": "Shell脚本",
            "extensions": [".sh", ".bash", ".zsh", ".ps1"],
            "directory": "scripts/shell",
            "confidence": 0.9
        },
        {
            "id": "configs",
            "name": "配置文件",
            "extensions": [".json", ".yaml", ".yml", ".conf", ".ini", ".env", ".toml"],
            "directory": "configs",
            "confidence": 0.85
        },
        {
            "id": "output_docs",
            "name": "输出文档",
            "extensions": [".md", ".txt", ".pdf", ".docx", ".html", ".rtf"],
            "directory": "output",
            "confidence": 0.8
        },
        {
            "id": "data_files",
            "name": "数据文件",
            "extensions": [".csv", ".xlsx", ".xls", ".parquet", ".db", ".sqlite", ".jsonl"],
            "directory": "data",
            "subdirs": ["raw", "processed", "external"],
            "confidence": 0.85
        },
        {
            "id": "temp_files",
            "name": "临时文件",
            "extensions": [".log", ".tmp", ".cache", ".bak", ".swp"],
            "directory": "temp",
            "confidence": 0.9
        },
        {
            "id": "docs",
            "name": "项目文档",
            "extensions": [".md"],
            "directory": "docs",
            "exclude_patterns": ["*report*", "*output*", "*result*"],
            "confidence": 0.75
        }
    ]
}

# 项目类型指示器
PROJECT_INDICATORS = {
    "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"],
    "nodejs": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
    "react": ["src/App.js", "src/App.jsx", "src/App.tsx", "public/index.html", "vite.config.js"],
    "vue": ["vue.config.js", "src/App.vue", "vite.config.js"],
    "angular": ["angular.json", "src/app/app.component.ts"],
    "go": ["go.mod", "go.sum"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "java": ["pom.xml", "build.gradle", "gradlew"],
    "dotnet": [".csproj", ".sln"],
    "php": ["composer.json", "composer.lock"]
}

# 外部项目标志
EXTERNAL_INDICATORS = [
    ".git",
    "LICENSE",
    "README.md",
    "CONTRIBUTING.md",
    ".github",
    ".gitlab-ci.yml"
]


def load_rules(rules_path: Optional[Path] = None) -> Dict:
    """加载分类规则"""
    if rules_path is None:
        # 尝试多个位置
        possible_paths = [
            Path("organization-rules.json"),
            Path(".claude/organization-rules.json"),
            Path(".openclaw/skills/file-organizer/rules/default-rules.json"),
            Path.home() / ".openclaw/skills/file-organizer/rules/default-rules.json"
        ]
        for path in possible_paths:
            if path.exists():
                rules_path = path
                break

    if rules_path and rules_path.exists():
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    return DEFAULT_RULES


def detect_project_type(path: Path = Path(".")) -> Tuple[Optional[str], float]:
    """
    检测项目类型
    返回: (project_type, confidence)
    """
    detected_types = []

    for project_type, indicators in PROJECT_INDICATORS.items():
        for indicator in indicators:
            if (path / indicator).exists():
                detected_types.append(project_type)
                break

    if not detected_types:
        return None, 0.0

    # 如果有多个检测结果，选择第一个（最具体的）
    # 置信度根据检测到的指示器数量调整
    primary_type = detected_types[0]
    confidence = min(0.5 + 0.1 * len(detected_types), 0.9)

    return primary_type, confidence


def detect_external_project(path: Path = Path(".")) -> Tuple[bool, List[str], float]:
    """
    检测是否为外部引入的完整项目
    返回: (is_external, indicators_found, confidence)
    """
    indicators_found = []

    for indicator in EXTERNAL_INDICATORS:
        if (path / indicator).exists():
            indicators_found.append(indicator)

    # 检测到2个以上标志视为外部项目
    is_external = len(indicators_found) >= 2
    confidence = min(len(indicators_found) * 0.3, 1.0)

    return is_external, indicators_found, confidence


def analyze_file_content(content: Optional[str], filename: str) -> Tuple[Optional[str], float]:
    """
    分析文件内容推断类型
    返回: (inferred_type, confidence)
    """
    if not content:
        return None, 0.0

    content_indicators = {
        "react": ["import React", "from 'react'", "from \"react\"", "React.Component"],
        "vue": ["import Vue", "createApp", "Vue.component"],
        "angular": ["@Component", "@Injectable", "angular"],
        "python_web": ["from flask", "from django", "from fastapi"],
        "python_data": ["import pandas", "import numpy", "matplotlib", "sklearn"],
    }

    content_lower = content.lower()
    detected_types = []

    for file_type, indicators in content_indicators.items():
        for indicator in indicators:
            if indicator.lower() in content_lower:
                detected_types.append(file_type)
                break

    if detected_types:
        # 返回第一个检测到的类型
        return detected_types[0], 0.8

    return None, 0.0


def choose_subdirectory(rule: Dict, filename: str, content: Optional[str] = None) -> str:
    """
    为需要子目录的规则选择具体子目录
    """
    if "subdirs" not in rule:
        return rule["directory"]

    subdirs = rule["subdirs"]
    filename_lower = filename.lower()

    # data/ 目录的特殊逻辑
    if rule["id"] == "data_files":
        # 根据文件名关键词选择
        if any(k in filename_lower for k in ["raw", "source", "origin", "原始"]):
            return f"{rule['directory']}/raw"
        elif any(k in filename_lower for k in ["processed", "clean", "final", "处理"]):
            return f"{rule['directory']}/processed"
        elif any(k in filename_lower for k in ["external", "download", "import", "外部"]):
            return f"{rule['directory']}/external"
        else:
            # 新数据默认放入 raw
            return f"{rule['directory']}/raw"

    # 其他有子目录的规则
    return f"{rule['directory']}/{subdirs[0]}"


def auto_classify(
    filename: str,
    content: Optional[str] = None,
    current_dir: Path = Path("."),
    rules: Optional[Dict] = None
) -> Dict:
    """
    自动分类决策主函数

    返回结果格式:
    {
        "filename": str,
        "target_directory": str,
        "target_path": str,
        "rule_id": str,
        "confidence": float,
        "reason": str,
        "project_type": Optional[str],
        "suggested_rename": Optional[str],
        "auto_execute": bool
    }
    """
    if rules is None:
        rules = load_rules()

    ext = Path(filename).suffix.lower()
    result = {
        "filename": filename,
        "target_directory": None,
        "target_path": None,
        "rule_id": None,
        "confidence": 0.0,
        "reason": "",
        "project_type": None,
        "suggested_rename": None,
        "auto_execute": False,
        "timestamp": datetime.now().isoformat()
    }

    # 1. 基于扩展名匹配规则
    for rule in rules.get("rules", []):
        if ext in rule.get("extensions", []):
            # 检查排除模式
            excluded = False
            for pattern in rule.get("exclude_patterns", []):
                if re.search(pattern.replace("*", ".*"), filename, re.IGNORECASE):
                    excluded = True
                    break

            if not excluded:
                result["rule_id"] = rule["id"]
                result["confidence"] = rule.get("confidence", 0.8)
                result["reason"] = f"Extension '{ext}' matches rule '{rule['id']}'"

                # 选择子目录
                result["target_directory"] = choose_subdirectory(rule, filename, content)
                break

    # 2. 如果没有匹配到规则，尝试内容分析
    if result["rule_id"] is None and content:
        inferred_type, content_confidence = analyze_file_content(content, filename)
        if inferred_type:
            # 根据推断类型映射到目录
            type_to_dir = {
                "react": "src/components",
                "vue": "src/components",
                "angular": "src/app",
                "python_web": "app",
                "python_data": "scripts/python"
            }
            if inferred_type in type_to_dir:
                result["target_directory"] = type_to_dir[inferred_type]
                result["confidence"] = content_confidence
                result["reason"] = f"Content analysis suggests {inferred_type}"

    # 3. 如果仍然没有匹配，使用项目类型推断
    if result["target_directory"] is None:
        project_type, project_confidence = detect_project_type(current_dir)
        result["project_type"] = project_type

        if project_type:
            project_dirs = {
                "python": "scripts/python",
                "nodejs": "scripts",
                "react": "src",
                "vue": "src",
                "go": "cmd",
                "rust": "src"
            }
            if project_type in project_dirs:
                result["target_directory"] = project_dirs[project_type]
                result["confidence"] = project_confidence
                result["reason"] = f"Inferred from project type: {project_type}"

    # 4. 最后的默认位置
    if result["target_directory"] is None:
        result["target_directory"] = "misc"
        result["confidence"] = 0.5
        result["reason"] = "No specific rule matched, using default"

    # 构建完整路径
    result["target_path"] = f"{result['target_directory']}/{filename}"

    # 5. 检查目标路径是否已存在
    target_full_path = current_dir / result["target_path"]
    if target_full_path.exists():
        # 生成带时间戳的新文件名
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{stem}_{timestamp}{suffix}"
        result["suggested_rename"] = new_filename
        result["target_path"] = f"{result['target_directory']}/{new_filename}"
        result["reason"] += f" (renamed to avoid conflict: {new_filename})"

    return result


def should_auto_execute(classification: Dict, context: Dict) -> bool:
    """
    根据分类结果和上下文决定是否自动执行

    context 可能包含:
    - agent_auto_create: bool (是否 OpenClaw 自动创建)
    - mode: str (conservative/balanced/aggressive)
    - external_project: bool (是否外部项目)
    """
    confidence = classification.get("confidence", 0)
    mode = context.get("mode", "balanced")

    # 外部项目：不自动执行
    if context.get("external_project"):
        return False

    # 根据模式决定
    thresholds = {
        "conservative": 1.0,    # 从不自动执行
        "balanced": 0.7,        # 置信度 > 0.7
        "aggressive": 0.5       # 置信度 > 0.5
    }

    threshold = thresholds.get(mode, 0.7)

    # 保守模式：只有用户明确说"自动整理"才执行
    if mode == "conservative":
        return context.get("user_explicit_auto", False)

    # 其他模式：基于置信度
    return confidence >= threshold


def generate_operation_log(classification: Dict, executed: bool) -> Dict:
    """生成操作日志"""
    log_id = f"ORG-{datetime.now().strftime('%Y%m%d')}-{generate_sequence_id()}"

    return {
        "id": log_id,
        "timestamp": classification["timestamp"],
        "operation": "CLASSIFY",
        "filename": classification["filename"],
        "target_directory": classification["target_directory"],
        "target_path": classification["target_path"],
        "rule_id": classification["rule_id"],
        "confidence": classification["confidence"],
        "reason": classification["reason"],
        "executed": executed,
        "status": "completed" if executed else "suggested"
    }


def generate_sequence_id() -> str:
    """生成序列ID (001-999)"""
    # 简化实现：使用时间微秒的后3位
    import random
    return f"{random.randint(1, 999):03d}"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="自动分类决策器 - OpenClaw File Organizer"
    )
    parser.add_argument("filename", help="要分类的文件名")
    parser.add_argument("--content", "-c", help="文件内容预览（用于内容分析）")
    parser.add_argument("--content-file", "-f", help="包含文件内容的文件路径")
    parser.add_argument("--rules", "-r", help="规则文件路径")
    parser.add_argument("--project-dir", "-d", default=".", help="项目目录")
    parser.add_argument("--mode", "-m", default="balanced",
                        choices=["conservative", "balanced", "aggressive"],
                        help="运行模式")
    parser.add_argument("--agent-auto", "-a", action="store_true",
                        help="OpenClaw 自动创建模式")
    parser.add_argument("--output", "-o", choices=["json", "text"], default="json",
                        help="输出格式")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅分析，不生成执行建议")

    args = parser.parse_args()

    # 读取内容
    content = args.content
    if args.content_file:
        try:
            with open(args.content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read content file: {e}", file=sys.stderr)

    # 加载规则
    rules = load_rules(Path(args.rules) if args.rules else None)

    # 执行分类
    project_dir = Path(args.project_dir).resolve()
    classification = auto_classify(args.filename, content, project_dir, rules)

    # 检测外部项目
    is_external, external_indicators, external_confidence = detect_external_project(project_dir)

    # 构建上下文
    context = {
        "agent_auto_create": args.agent_auto,
        "mode": args.mode,
        "external_project": is_external
    }

    # 决定是否自动执行
    classification["auto_execute"] = should_auto_execute(classification, context)
    classification["external_project_detected"] = is_external
    classification["external_indicators"] = external_indicators if is_external else []

    # 输出结果
    if args.output == "json":
        print(json.dumps(classification, indent=2, ensure_ascii=False))
    else:
        print(f"📄 文件: {classification['filename']}")
        print(f"📁 目标目录: {classification['target_directory']}")
        print(f"🎯 完整路径: {classification['target_path']}")
        print(f"📊 置信度: {classification['confidence']:.2f}")
        print(f"💡 理由: {classification['reason']}")
        print(f"🤖 自动执行: {'是' if classification['auto_execute'] else '否'}")
        if is_external:
            print(f"⚠️  外部项目: 检测到 {len(external_indicators)} 个标志")

    return 0 if classification["target_directory"] else 1


if __name__ == "__main__":
    sys.exit(main())
