"""
Pylint Tool - 代码质量检查工具封装
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import BaseTool


class PylintTool(BaseTool):
    """
    Pylint 代码质量检查工具

    检测内容:
    - 代码质量问题
    - 重复代码检测
    - 代码规范
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        enable_similarity: bool = True,
        min_similarity_lines: int = 10
    ):
        super().__init__(config_path)
        self.enable_similarity = enable_similarity
        self.min_similarity_lines = min_similarity_lines

    @property
    def name(self) -> str:
        return "pylint"

    @property
    def description(self) -> str:
        return "Python 代码质量分析与重复检测"

    def build_command(self, targets: List[Path]) -> str:
        targets_str = " ".join(str(t) for t in targets)

        if self.config_path and self.config_path.exists():
            return f"pylint --rcfile={self.config_path} {targets_str}"

        # 使用内置参数
        cmd_parts = [
            "pylint",
            "--disable=C0111,C0103,R0903,R0913,W0212",
            f"--min-similarity-lines={self.min_similarity_lines}",
            "--ignore-comments=yes",
            "--ignore-docstrings=yes",
            "--ignore-imports=yes",
        ]

        if self.enable_similarity:
            cmd_parts.append("--enable=similarities")

        cmd_parts.append(targets_str)
        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        解析 Pylint 输出

        Returns:
            {
                'issue_count': int,
                'duplicate_blocks': int,
                'score': float,
                'issues_by_type': {'warning': 10, 'error': 5, ...}
            }
        """
        # 统计重复代码块
        duplicate_blocks = output.count('Similar lines')

        # 提取评分
        score = 0.0
        score_match = re.search(r'rated at ([\d.]+)/10', output)
        if score_match:
            score = float(score_match.group(1))

        # 统计问题类型
        issues_by_type: Dict[str, int] = {}
        type_patterns = [
            (r'(\d+) error', 'error'),
            (r'(\d+) warning', 'warning'),
            (r'(\d+) refactor', 'refactor'),
            (r'(\d+) convention', 'convention'),
        ]

        for pattern, issue_type in type_patterns:
            match = re.search(pattern, output)
            if match:
                issues_by_type[issue_type] = int(match.group(1))

        total_issues = sum(issues_by_type.values())

        return {
            'issue_count': total_issues,
            'duplicate_blocks': duplicate_blocks,
            'score': score,
            'issues_by_type': issues_by_type
        }

