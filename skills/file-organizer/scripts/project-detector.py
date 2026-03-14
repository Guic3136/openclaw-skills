#!/usr/bin/env python3
"""
项目类型检测器 - OpenClaw File Organizer Skill

检测当前工作区的项目类型，帮助自动分类器做出更准确的决策。

Author: Leo Baher
Version: 1.0.0
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class ProjectType(Enum):
    """支持的项目类型"""
    PYTHON = "python"
    NODEJS = "nodejs"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    DOTNET = "dotnet"
    PHP = "php"
    RUBY = "ruby"
    FLUTTER = "flutter"
    UNITY = "unity"
    GENERIC = "generic"


@dataclass
class ProjectInfo:
    """项目信息"""
    type: str
    name: Optional[str]
    version: Optional[str]
    confidence: float
    indicators_found: List[str]
    primary_language: Optional[str]
    framework: Optional[str]
    is_external: bool
    external_indicators: List[str]
    suggested_structure: Dict[str, str]


# 项目类型检测规则
PROJECT_RULES = {
    ProjectType.PYTHON: {
        "indicators": [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "poetry.lock",
            "setup.cfg",
            "tox.ini",
            ".python-version"
        ],
        "primary_language": "Python",
        "common_dirs": ["src", "scripts", "tests", "docs", "notebooks"],
        "file_extensions": [".py", ".ipynb", ".pyw"]
    },
    ProjectType.NODEJS: {
        "indicators": [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "npm-shrinkwrap.json",
            ".npmrc",
            ".nvmrc"
        ],
        "primary_language": "JavaScript",
        "common_dirs": ["src", "lib", "dist", "node_modules", "scripts"],
        "file_extensions": [".js", ".mjs", ".cjs"]
    },
    ProjectType.REACT: {
        "indicators": [
            "src/App.js",
            "src/App.jsx",
            "src/App.tsx",
            "public/index.html",
            "vite.config.js",
            "vite.config.ts",
            "craco.config.js",
            "src/index.js",
            "src/main.jsx"
        ],
        "primary_language": "JavaScript/TypeScript",
        "framework": "React",
        "parent_type": ProjectType.NODEJS,
        "common_dirs": ["src/components", "src/pages", "src/hooks", "src/utils", "public"],
        "file_extensions": [".jsx", ".tsx"]
    },
    ProjectType.VUE: {
        "indicators": [
            "vue.config.js",
            "vite.config.js",
            "src/App.vue",
            "src/main.js",
            ".vuerc"
        ],
        "primary_language": "JavaScript",
        "framework": "Vue",
        "parent_type": ProjectType.NODEJS,
        "common_dirs": ["src/components", "src/views", "src/store", "src/router"],
        "file_extensions": [".vue"]
    },
    ProjectType.ANGULAR: {
        "indicators": [
            "angular.json",
            "src/app/app.component.ts",
            "src/app/app.module.ts",
            ".angular-cli.json"
        ],
        "primary_language": "TypeScript",
        "framework": "Angular",
        "parent_type": ProjectType.NODEJS,
        "common_dirs": ["src/app", "src/assets", "src/environments"],
        "file_extensions": [".ts"]
    },
    ProjectType.GO: {
        "indicators": [
            "go.mod",
            "go.sum",
            "go.work",
            ".go-version",
            "Makefile"  # Go 项目常用
        ],
        "primary_language": "Go",
        "common_dirs": ["cmd", "pkg", "internal", "api", "web", "scripts"],
        "file_extensions": [".go"]
    },
    ProjectType.RUST: {
        "indicators": [
            "Cargo.toml",
            "Cargo.lock",
            "rust-toolchain",
            ".rustfmt.toml"
        ],
        "primary_language": "Rust",
        "common_dirs": ["src", "tests", "examples", "benches"],
        "file_extensions": [".rs"]
    },
    ProjectType.JAVA: {
        "indicators": [
            "pom.xml",
            "build.gradle",
            "gradlew",
            "settings.gradle",
            "build.gradle.kts"
        ],
        "primary_language": "Java/Kotlin",
        "common_dirs": ["src/main/java", "src/test/java", "src/main/resources"],
        "file_extensions": [".java", ".kt"]
    },
    ProjectType.DOTNET: {
        "indicators": [
            ".csproj",
            ".sln",
            ".fsproj",
            ".vbproj",
            "global.json"
        ],
        "primary_language": "C#/F#/VB",
        "common_dirs": ["src", "tests", "docs"],
        "file_extensions": [".cs", ".fs", ".vb"]
    },
    ProjectType.PHP: {
        "indicators": [
            "composer.json",
            "composer.lock",
            "artisan",  # Laravel
            "symfony.lock"  # Symfony
        ],
        "primary_language": "PHP",
        "common_dirs": ["src", "app", "config", "public", "tests"],
        "file_extensions": [".php"]
    },
    ProjectType.RUBY: {
        "indicators": [
            "Gemfile",
            "Gemfile.lock",
            "Rakefile",
            ".ruby-version",
            "config.ru"
        ],
        "primary_language": "Ruby",
        "common_dirs": ["lib", "app", "config", "test", "spec"],
        "file_extensions": [".rb"]
    },
    ProjectType.FLUTTER: {
        "indicators": [
            "pubspec.yaml",
            "lib/main.dart",
            "android/app",
            "ios/Runner"
        ],
        "primary_language": "Dart",
        "framework": "Flutter",
        "common_dirs": ["lib", "test", "android", "ios", "web"],
        "file_extensions": [".dart"]
    },
    ProjectType.UNITY: {
        "indicators": [
            "Assets/",
            "ProjectSettings/",
            "Packages/manifest.json"
        ],
        "primary_language": "C#",
        "framework": "Unity",
        "common_dirs": ["Assets/Scripts", "Assets/Scenes", "Packages"],
        "file_extensions": [".cs", ".unity"]
    }
}

# 外部项目标志
EXTERNAL_INDICATORS = {
    "files": [
        ".git",
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "COPYING",
        "README.md",
        "README.rst",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "CHANGELOG.md",
        "SECURITY.md",
        ".github",
        ".gitlab-ci.yml",
        ".travis.yml",
        ".circleci",
        "Jenkinsfile"
    ],
    "threshold": 2  # 发现2个以上视为外部项目
}


def check_indicator_exists(path: Path, indicator: str) -> bool:
    """检查指示器是否存在"""
    # 支持文件和目录
    target = path / indicator
    return target.exists()


def detect_single_type(path: Path, project_type: ProjectType, rules: Dict) -> Tuple[int, List[str]]:
    """
    检测单一项目类型
    返回: (匹配数量, 匹配到的指示器列表)
    """
    indicators = rules.get("indicators", [])
    found = []

    for indicator in indicators:
        if check_indicator_exists(path, indicator):
            found.append(indicator)

    return len(found), found


def detect_project_type(path: Path = Path(".")) -> Tuple[ProjectType, float, List[str], Optional[ProjectType]]:
    """
    检测项目类型

    返回: (项目类型, 置信度, 匹配指示器, 父类型)
    """
    scores = {}
    all_indicators = {}

    # 计算每种类型的匹配分数
    for project_type, rules in PROJECT_RULES.items():
        count, indicators = detect_single_type(path, project_type, rules)
        if count > 0:
            scores[project_type] = count
            all_indicators[project_type] = indicators

    if not scores:
        return ProjectType.GENERIC, 0.0, [], None

    # 找到最高分
    max_score = max(scores.values())
    best_types = [t for t, s in scores.items() if s == max_score]

    # 如果有多个相同分数，选择更具体的（有parent_type的）
    best_type = best_types[0]
    if len(best_types) > 1:
        # 优先选择框架类型（React > Node.js）
        for t in best_types:
            if "framework" in PROJECT_RULES[t]:
                best_type = t
                break

    # 计算置信度
    # 基础置信度：匹配数量 * 0.3，最高0.9
    base_confidence = min(max_score * 0.3, 0.9)

    # 如果有父类型，稍微降低置信度（因为是推断的）
    parent_type = PROJECT_RULES[best_type].get("parent_type")
    if parent_type and parent_type in scores:
        base_confidence *= 0.9

    return best_type, base_confidence, all_indicators[best_type], parent_type


def detect_external_project(path: Path = Path(".")) -> Tuple[bool, List[str], float]:
    """
    检测是否为外部引入的完整项目

    返回: (是否外部项目, 发现的标志, 置信度)
    """
    found = []

    for indicator in EXTERNAL_INDICATORS["files"]:
        if check_indicator_exists(path, indicator):
            found.append(indicator)

    count = len(found)
    threshold = EXTERNAL_INDICATORS["threshold"]

    is_external = count >= threshold
    confidence = min(count * 0.3, 1.0)

    return is_external, found, confidence


def get_project_name(path: Path) -> Optional[str]:
    """尝试获取项目名称"""
    # 尝试从配置文件读取

    # package.json (Node.js)
    package_json = path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("name")
        except:
            pass

    # pyproject.toml (Python)
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        try:
            with open(pyproject, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("name"):
                        return line.split("=")[1].strip().strip('"')
        except:
            pass

    # Cargo.toml (Rust)
    cargo_toml = path / "Cargo.toml"
    if cargo_toml.exists():
        try:
            with open(cargo_toml, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("name"):
                        return line.split("=")[1].strip().strip('"')
        except:
            pass

    # 使用目录名
    return path.name if path.name != "." else None


def get_project_version(path: Path, project_type: ProjectType) -> Optional[str]:
    """尝试获取项目版本"""
    version_files = {
        ProjectType.NODEJS: "package.json",
        ProjectType.REACT: "package.json",
        ProjectType.VUE: "package.json",
        ProjectType.ANGULAR: "package.json",
        ProjectType.PYTHON: "pyproject.toml",
        ProjectType.RUST: "Cargo.toml"
    }

    filename = version_files.get(project_type)
    if not filename:
        return None

    filepath = path / filename
    if not filepath.exists():
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            if filename.endswith('.json'):
                data = json.load(f)
                return data.get("version")
            else:
                # TOML 文件简单解析
                for line in f:
                    if line.startswith("version"):
                        return line.split("=")[1].strip().strip('"')
    except:
        pass

    return None


def get_suggested_structure(project_type: ProjectType, rules: Dict) -> Dict[str, str]:
    """获取建议的目录结构"""
    common_dirs = rules.get("common_dirs", [])

    # 通用映射
    structure = {
        "code": "src",
        "config": "configs",
        "docs": "docs",
        "tests": "tests",
        "scripts": "scripts",
        "data": "data",
        "output": "output",
        "temp": "temp"
    }

    # 根据项目类型调整
    type_mappings = {
        ProjectType.PYTHON: {
            "code": "src or scripts/python",
            "notebooks": "notebooks"
        },
        ProjectType.NODEJS: {
            "code": "src or lib",
            "build": "dist or build"
        },
        ProjectType.REACT: {
            "code": "src",
            "components": "src/components",
            "pages": "src/pages",
            "assets": "public or src/assets"
        },
        ProjectType.GO: {
            "code": "cmd, pkg, internal",
            "api": "api"
        },
        ProjectType.RUST: {
            "code": "src",
            "examples": "examples"
        },
        ProjectType.JAVA: {
            "code": "src/main/java",
            "resources": "src/main/resources",
            "tests": "src/test/java"
        }
    }

    if project_type in type_mappings:
        structure.update(type_mappings[project_type])

    return structure


def analyze_project(path: Path = Path(".")) -> ProjectInfo:
    """
    全面分析项目

    返回完整的 ProjectInfo
    """
    # 检测项目类型
    project_type, confidence, indicators, parent_type = detect_project_type(path)
    rules = PROJECT_RULES.get(project_type, {})

    # 检测外部项目
    is_external, external_indicators, external_confidence = detect_external_project(path)

    # 获取项目信息
    name = get_project_name(path)
    version = get_project_version(path, project_type)

    # 获取建议结构
    suggested_structure = get_suggested_structure(project_type, rules)

    return ProjectInfo(
        type=project_type.value,
        name=name,
        version=version,
        confidence=confidence,
        indicators_found=indicators,
        primary_language=rules.get("primary_language"),
        framework=rules.get("framework"),
        is_external=is_external,
        external_indicators=external_indicators,
        suggested_structure=suggested_structure
    )


def print_project_info(info: ProjectInfo, output_format: str = "text"):
    """输出项目信息"""
    if output_format == "json":
        print(json.dumps(asdict(info), indent=2, ensure_ascii=False))
    else:
        print("📊 项目分析结果")
        print("=" * 50)
        print(f"类型: {info.type}")
        if info.framework:
            print(f"框架: {info.framework}")
        print(f"主要语言: {info.primary_language or '未知'}")
        if info.name:
            print(f"项目名称: {info.name}")
        if info.version:
            print(f"版本: {info.version}")
        print(f"置信度: {info.confidence:.2%}")
        print()
        print("检测到的标志:")
        for indicator in info.indicators_found:
            print(f"  ✓ {indicator}")
        print()
        if info.is_external:
            print("⚠️  外部项目检测:")
            print(f"  置信度: {len(info.external_indicators) * 30}%")
            print("  发现的标志:")
            for indicator in info.external_indicators:
                print(f"    - {indicator}")
            print()
        print("建议的目录结构:")
        for category, directory in info.suggested_structure.items():
            print(f"  {category}: {directory}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="项目类型检测器 - OpenClaw File Organizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 检测当前目录
  %(prog)s -p /path/to/project       # 检测指定目录
  %(prog)s -o json                   # JSON 格式输出
  %(prog)s --external-only           # 仅检测外部项目
        """
    )
    parser.add_argument("--path", "-p", default=".", help="项目路径 (默认: 当前目录)")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text",
                        help="输出格式")
    parser.add_argument("--external-only", "-e", action="store_true",
                        help="仅检测是否为外部项目")
    parser.add_argument("--type-only", "-t", action="store_true",
                        help="仅输出项目类型")

    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.exists():
        print(f"❌ 错误: 路径不存在 {project_path}", file=sys.stderr)
        sys.exit(1)

    if args.external_only:
        is_external, indicators, confidence = detect_external_project(project_path)
        if args.output == "json":
            print(json.dumps({
                "is_external": is_external,
                "indicators": indicators,
                "confidence": confidence
            }, indent=2))
        else:
            status = "是" if is_external else "否"
            print(f"外部项目: {status}")
            if is_external:
                print(f"发现标志: {', '.join(indicators)}")
        sys.exit(0)

    if args.type_only:
        project_type, confidence, _, _ = detect_project_type(project_path)
        print(project_type.value)
        sys.exit(0)

    # 完整分析
    info = analyze_project(project_path)
    print_project_info(info, args.output)

    # 返回退出码（外部项目返回1，便于脚本判断）
    if info.is_external:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
