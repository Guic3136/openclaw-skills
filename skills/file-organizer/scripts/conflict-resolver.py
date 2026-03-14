#!/usr/bin/env python3
"""
冲突解决器 - OpenClaw File Organizer Skill

处理文件移动中的各种冲突：
1. 目标路径已存在
2. 文件名冲突
3. 目录权限问题
4. 生成回滚脚本

Author: Leo Baher
Version: 1.0.0
"""

import json
import sys
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class ConflictType(Enum):
    """冲突类型"""
    PATH_EXISTS = "path_exists"           # 目标路径已存在
    NAME_COLLISION = "name_collision"     # 文件名冲突
    PERMISSION_DENIED = "permission_denied"  # 权限不足
    DIRECTORY_NOT_EMPTY = "dir_not_empty" # 目录非空
    UNKNOWN = "unknown"                   # 未知错误


class ResolutionStrategy(Enum):
    """解决策略"""
    RENAME_WITH_TIMESTAMP = "timestamp"   # 时间戳重命名
    RENAME_WITH_SEQUENCE = "sequence"     # 序号重命名
    RENAME_WITH_HASH = "hash"             # 哈希重命名
    OVERWRITE = "overwrite"               # 覆盖（危险）
    SKIP = "skip"                         # 跳过
    MERGE = "merge"                       # 合并（目录）
    PROMPT = "prompt"                     # 询问用户


@dataclass
class ConflictInfo:
    """冲突信息"""
    conflict_type: ConflictType
    source_path: Path
    target_path: Path
    existing_file_info: Optional[Dict]
    message: str


@dataclass
class ResolutionResult:
    """解决结果"""
    success: bool
    final_target: Optional[Path]
    strategy_used: ResolutionStrategy
    original_target: Path
    conflict_info: ConflictInfo
    message: str
    requires_user_input: bool = False


@dataclass
class OperationRecord:
    """操作记录"""
    timestamp: str
    operation_id: str
    action: str  # MOVE, COPY, MKDIR
    source: str
    target: str
    source_hash: Optional[str]
    target_hash: Optional[str]
    status: str  # pending, completed, failed, rolled_back
    rollback_command: str


class ConflictResolver:
    """冲突解决器"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or (Path.home() / ".openclaw" / "skills" / "file-organizer" / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.operations: List[OperationRecord] = []

    def detect_conflict(self, source: Path, target: Path) -> Optional[ConflictInfo]:
        """
        检测可能的冲突

        返回 None 表示无冲突，否则返回 ConflictInfo
        """
        # 检查目标是否已存在
        if target.exists():
            existing_info = self._get_file_info(target)

            if target.is_file():
                return ConflictInfo(
                    conflict_type=ConflictType.PATH_EXISTS,
                    source_path=source,
                    target_path=target,
                    existing_file_info=existing_info,
                    message=f"目标文件已存在: {target}"
                )
            elif target.is_dir():
                return ConflictInfo(
                    conflict_type=ConflictType.PATH_EXISTS,
                    source_path=source,
                    target_path=target,
                    existing_file_info=existing_info,
                    message=f"目标目录已存在: {target}"
                )

        # 检查父目录权限
        parent = target.parent
        if parent.exists() and not os.access(parent, os.W_OK):
            return ConflictInfo(
                conflict_type=ConflictType.PERMISSION_DENIED,
                source_path=source,
                target_path=target,
                existing_file_info=None,
                message=f"无写入权限: {parent}"
            )

        return None

    def resolve_conflict(
        self,
        conflict: ConflictInfo,
        strategy: ResolutionStrategy = ResolutionStrategy.RENAME_WITH_TIMESTAMP,
        user_callback: Optional[Callable] = None
    ) -> ResolutionResult:
        """
        解决冲突

        根据策略自动解决或询问用户
        """
        if strategy == ResolutionStrategy.PROMPT and user_callback:
            return user_callback(conflict)

        if conflict.conflict_type == ConflictType.PATH_EXISTS:
            return self._resolve_path_exists(conflict, strategy)

        if conflict.conflict_type == ConflictType.PERMISSION_DENIED:
            return ResolutionResult(
                success=False,
                final_target=None,
                strategy_used=strategy,
                original_target=conflict.target_path,
                conflict_info=conflict,
                message=f"无法解决权限问题: {conflict.message}",
                requires_user_input=False
            )

        return ResolutionResult(
            success=False,
            final_target=None,
            strategy_used=strategy,
            original_target=conflict.target_path,
            conflict_info=conflict,
            message=f"未处理的冲突类型: {conflict.conflict_type}"
        )

    def _resolve_path_exists(
        self,
        conflict: ConflictInfo,
        strategy: ResolutionStrategy
    ) -> ResolutionResult:
        """解决路径已存在的冲突"""
        target = conflict.target_path

        if strategy == ResolutionStrategy.SKIP:
            return ResolutionResult(
                success=False,
                final_target=None,
                strategy_used=strategy,
                original_target=target,
                conflict_info=conflict,
                message="用户选择跳过此文件"
            )

        if strategy == ResolutionStrategy.OVERWRITE:
            # 覆盖模式 - 危险，需要额外确认
            return ResolutionResult(
                success=True,
                final_target=target,
                strategy_used=strategy,
                original_target=target,
                conflict_info=conflict,
                message=f"将覆盖现有文件: {target}",
                requires_user_input=True  # 需要用户确认
            )

        if strategy == ResolutionStrategy.RENAME_WITH_TIMESTAMP:
            new_target = self._generate_timestamped_name(target)
            return ResolutionResult(
                success=True,
                final_target=new_target,
                strategy_used=strategy,
                original_target=target,
                conflict_info=conflict,
                message=f"使用时间戳重命名: {target.name} -> {new_target.name}"
            )

        if strategy == ResolutionStrategy.RENAME_WITH_SEQUENCE:
            new_target = self._generate_sequenced_name(target)
            return ResolutionResult(
                success=True,
                final_target=new_target,
                strategy_used=strategy,
                original_target=target,
                conflict_info=conflict,
                message=f"使用序号重命名: {target.name} -> {new_target.name}"
            )

        if strategy == ResolutionStrategy.RENAME_WITH_HASH:
            new_target = self._generate_hashed_name(target, conflict.source_path)
            return ResolutionResult(
                success=True,
                final_target=new_target,
                strategy_used=strategy,
                original_target=target,
                conflict_info=conflict,
                message=f"使用哈希重命名: {target.name} -> {new_target.name}"
            )

        return ResolutionResult(
            success=False,
            final_target=None,
            strategy_used=strategy,
            original_target=target,
            conflict_info=conflict,
            message=f"未知的解决策略: {strategy}"
        )

    def _generate_timestamped_name(self, target: Path) -> Path:
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = target.stem
        suffix = target.suffix
        new_name = f"{stem}_{timestamp}{suffix}"
        return target.parent / new_name

    def _generate_sequenced_name(self, target: Path, start: int = 1) -> Path:
        """生成带序号的文件名"""
        stem = target.stem
        suffix = target.suffix
        parent = target.parent

        seq = start
        while True:
            new_name = f"{stem}_{seq:03d}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            seq += 1
            if seq > 999:  # 防止无限循环
                # 回退到时间戳
                return self._generate_timestamped_name(target)

    def _generate_hashed_name(self, target: Path, source: Path) -> Path:
        """生成带哈希的文件名"""
        file_hash = self._calculate_hash(source)[:8]
        stem = target.stem
        suffix = target.suffix
        new_name = f"{stem}_{file_hash}{suffix}"
        return target.parent / new_name

    def _calculate_hash(self, filepath: Path) -> str:
        """计算文件哈希"""
        if not filepath.exists():
            return ""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _get_file_info(self, filepath: Path) -> Dict:
        """获取文件信息"""
        try:
            stat = filepath.stat()
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": self._calculate_hash(filepath) if filepath.is_file() else None,
                "type": "file" if filepath.is_file() else "directory"
            }
        except Exception as e:
            return {"error": str(e)}

    def execute_with_record(
        self,
        source: Path,
        target: Path,
        action: str = "MOVE"
    ) -> Tuple[bool, str]:
        """
        执行文件操作并记录

        返回: (success, message)
        """
        # 先检测冲突
        conflict = self.detect_conflict(source, target)

        if conflict:
            # 自动使用默认策略解决
            result = self.resolve_conflict(conflict, ResolutionStrategy.RENAME_WITH_TIMESTAMP)

            if not result.success:
                return False, f"无法解决冲突: {result.message}"

            if result.requires_user_input:
                return False, f"需要用户确认: {result.message}"

            # 使用解决后的目标路径
            target = result.final_target

        # 确保目标目录存在
        target.parent.mkdir(parents=True, exist_ok=True)

        # 记录操作前的状态
        source_hash = self._calculate_hash(source) if source.is_file() else None

        try:
            if action == "MOVE":
                shutil.move(str(source), str(target))
            elif action == "COPY":
                if source.is_dir():
                    shutil.copytree(str(source), str(target))
                else:
                    shutil.copy2(str(source), str(target))
            elif action == "MKDIR":
                target.mkdir(parents=True, exist_ok=True)
            else:
                return False, f"未知的操作类型: {action}"

            # 记录操作
            target_hash = self._calculate_hash(target) if target.is_file() else None
            record = self._create_record(action, source, target, source_hash, target_hash)
            self.operations.append(record)
            self._save_record(record)

            return True, f"{action} 成功: {source} -> {target}"

        except Exception as e:
            return False, f"{action} 失败: {e}"

    def _create_record(
        self,
        action: str,
        source: Path,
        target: Path,
        source_hash: Optional[str],
        target_hash: Optional[str]
    ) -> OperationRecord:
        """创建操作记录"""
        timestamp = datetime.now().isoformat()
        op_id = f"ORG-{datetime.now().strftime('%Y%m%d')}-{len(self.operations)+1:03d}"

        # 生成回滚命令
        if action == "MOVE":
            rollback_cmd = f'mv "{target}" "{source}"'
        elif action == "COPY":
            rollback_cmd = f'rm -rf "{target}"  # COPY操作回滚：删除副本'
        elif action == "MKDIR":
            rollback_cmd = f'rmdir "{target}"  # MKDIR操作回滚：删除空目录'
        else:
            rollback_cmd = f'# 未知操作类型的回滚: {action}'

        return OperationRecord(
            timestamp=timestamp,
            operation_id=op_id,
            action=action,
            source=str(source),
            target=str(target),
            source_hash=source_hash,
            target_hash=target_hash,
            status="completed",
            rollback_command=rollback_cmd
        )

    def _save_record(self, record: OperationRecord):
        """保存操作记录到日志文件"""
        log_file = self.log_dir / f"operations_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + '\n')

    def generate_rollback_script(self, output_path: Optional[Path] = None) -> Path:
        """
        生成回滚脚本

        返回生成的脚本路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_path is None:
            output_path = self.log_dir / f"rollback_{timestamp}.sh"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write(f"# 回滚脚本 - 生成时间: {timestamp}\n")
            f.write(f"# 操作数量: {len(self.operations)}\n")
            f.write("# 按逆序执行以恢复到原始状态\n\n")

            # 逆序输出回滚命令
            for record in reversed(self.operations):
                f.write(f"# {record.operation_id}: {record.action}\n")
                f.write(f"# 时间: {record.timestamp}\n")
                f.write(f'{record.rollback_command}\n')
                f.write(f'echo "回滚 {record.operation_id} 完成"\n\n')

            f.write('echo "✓ 所有操作已回滚"\n')

        # 设置可执行权限（Unix系统）
        try:
            os.chmod(output_path, 0o755)
        except Exception:
            pass

        return output_path

    def preview_operations(self, operations: List[Dict]) -> str:
        """
        预览即将执行的操作

        返回格式化的预览文本
        """
        lines = [
            "📋 操作预览",
            "=" * 50,
            f"共 {len(operations)} 个操作:\n"
        ]

        for i, op in enumerate(operations, 1):
            action = op.get('action', 'UNKNOWN')
            source = op.get('source', 'N/A')
            target = op.get('target', 'N/A')

            lines.append(f"{i}. [{action}] {source}")
            lines.append(f"   -> {target}\n")

        lines.append("=" * 50)
        lines.append("确认后将执行以上操作并生成回滚脚本")

        return '\n'.join(lines)

    def get_operation_summary(self) -> Dict:
        """获取操作摘要"""
        return {
            "total_operations": len(self.operations),
            "move_count": sum(1 for op in self.operations if op.action == "MOVE"),
            "copy_count": sum(1 for op in self.operations if op.action == "COPY"),
            "mkdir_count": sum(1 for op in self.operations if op.action == "MKDIR"),
            "timestamp": datetime.now().isoformat()
        }


def resolve_path_conflict(
    source: str,
    target: str,
    strategy: str = "timestamp"
) -> Dict:
    """
    简单的命令行接口函数

    返回结果字典
    """
    resolver = ConflictResolver()

    source_path = Path(source).resolve()
    target_path = Path(target).resolve()

    # 检测冲突
    conflict = resolver.detect_conflict(source_path, target_path)

    if not conflict:
        return {
            "has_conflict": False,
            "final_target": str(target_path),
            "strategy": None,
            "message": "无冲突"
        }

    # 解析策略
    strategy_map = {
        "timestamp": ResolutionStrategy.RENAME_WITH_TIMESTAMP,
        "sequence": ResolutionStrategy.RENAME_WITH_SEQUENCE,
        "hash": ResolutionStrategy.RENAME_WITH_HASH,
        "overwrite": ResolutionStrategy.OVERWRITE,
        "skip": ResolutionStrategy.SKIP,
    }

    selected_strategy = strategy_map.get(strategy, ResolutionStrategy.RENAME_WITH_TIMESTAMP)

    # 解决冲突
    result = resolver.resolve_conflict(conflict, selected_strategy)

    return {
        "has_conflict": True,
        "conflict_type": conflict.conflict_type.value,
        "resolved": result.success,
        "final_target": str(result.final_target) if result.final_target else None,
        "strategy": result.strategy_used.value,
        "message": result.message,
        "requires_user_input": result.requires_user_input
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="冲突解决器 - OpenClaw File Organizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s /path/to/source.py /path/to/target.py
  %(prog)s ./script.py ./scripts/python/script.py --strategy timestamp
  %(prog)s --generate-rollback-only --log-dir ~/.openclaw/logs
        """
    )

    parser.add_argument("source", nargs="?", help="源文件路径")
    parser.add_argument("target", nargs="?", help="目标文件路径")
    parser.add_argument("--strategy", "-s", default="timestamp",
                        choices=["timestamp", "sequence", "hash", "overwrite", "skip"],
                        help="冲突解决策略 (默认: timestamp)")
    parser.add_argument("--execute", "-e", action="store_true",
                        help="实际执行移动操作并记录")
    parser.add_argument("--action", "-a", default="MOVE",
                        choices=["MOVE", "COPY", "MKDIR"],
                        help="操作类型")
    parser.add_argument("--log-dir", "-l", help="日志目录")
    parser.add_argument("--generate-rollback-only", "-r", action="store_true",
                        help="仅生成回滚脚本")
    parser.add_argument("--output", "-o", choices=["json", "text"], default="text",
                        help="输出格式")

    args = parser.parse_args()

    # 仅生成回滚脚本模式
    if args.generate_rollback_only:
        log_dir = Path(args.log_dir) if args.log_dir else None
        resolver = ConflictResolver(log_dir)
        script_path = resolver.generate_rollback_script()

        if args.output == "json":
            print(json.dumps({"rollback_script": str(script_path)}, indent=2))
        else:
            print(f"✓ 回滚脚本已生成: {script_path}")
        return 0

    # 检查参数
    if not args.source or not args.target:
        parser.print_help()
        return 1

    # 解析冲突
    result = resolve_path_conflict(args.source, args.target, args.strategy)

    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["has_conflict"]:
            print(f"⚠️  检测到冲突: {result['conflict_type']}")
            print(f"💡 解决策略: {result['strategy']}")
            print(f"📝 {result['message']}")
            if result['final_target']:
                print(f"📁 最终目标: {result['final_target']}")
            if result['requires_user_input']:
                print("⚠️  此操作需要用户确认")
        else:
            print(f"✓ {result['message']}")
            print(f"📁 目标: {result['final_target']}")

    # 执行模式
    if args.execute and (result["resolved"] or not result["has_conflict"]):
        log_dir = Path(args.log_dir) if args.log_dir else None
        resolver = ConflictResolver(log_dir)

        final_target = Path(result['final_target']) if result['final_target'] else Path(args.target)
        success, message = resolver.execute_with_record(
            Path(args.source),
            final_target,
            args.action
        )

        if args.output == "json":
            print(json.dumps({"executed": success, "message": message}, indent=2))
        else:
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")

        # 生成回滚脚本
        rollback_script = resolver.generate_rollback_script()
        if args.output != "json":
            print(f"📄 回滚脚本: {rollback_script}")

    return 0 if result["resolved"] or not result["has_conflict"] else 1


if __name__ == "__main__":
    sys.exit(main())
