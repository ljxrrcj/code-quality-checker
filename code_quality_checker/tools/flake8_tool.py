"""
Flake8 Tool - 代码风格检查工具封装
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import BaseTool


class Flake8Tool(BaseTool):
    """
    Flake8 代码风格检查工具

    检测内容:
    - PEP8 代码风格
    - 语法错误
    - 复杂度检查 (McCabe)
    - 常见 bug 模式 (flake8-bugbear)
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        max_line_length: int = 120,
        max_complexity: int = 10
    ):
        super().__init__(config_path)
        self.max_line_length = max_line_length
        self.max_complexity = max_complexity

    @property
    def name(self) -> str:
        return "flake8"

    @property
    def description(self) -> str:
        return "Python 代码风格检查 (PEP8)"

    def build_command(self, targets: List[Path]) -> str:
        targets_str = " ".join(str(t) for t in targets)

        if self.config_path and self.config_path.exists():
            return f"flake8 --config={self.config_path} {targets_str}"

        # 使用内置参数
        return (
            f"flake8 "
            f"--max-line-length={self.max_line_length} "
            f"--max-complexity={self.max_complexity} "
            f"--ignore=W503,E203 "
            f"--show-source "
            f"--statistics "
            f"{targets_str}"
        )

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        解析 Flake8 输出

        Returns:
            {
                'issue_count': int,
                'issues_by_code': {'E501': 10, 'W293': 5, ...},
                'issues_by_file': {'file.py': 15, ...}
            }
        """
        lines = [line.strip() for line in output.split('\n') if line.strip()]

        # 过滤掉统计行和空行
        issue_lines = [
            line for line in lines
            if line and not line.startswith('===') and ':' in line
        ]

        issues_by_code: Dict[str, int] = {}
        issues_by_file: Dict[str, int] = {}

        for line in issue_lines:
            # 格式: file.py:10:5: E501 line too long
            parts = line.split(':')
            if len(parts) >= 4:
                file_path = parts[0]
                message = ':'.join(parts[3:]).strip()

                # 提取错误码
                code = message.split()[0] if message else 'UNKNOWN'

                issues_by_code[code] = issues_by_code.get(code, 0) + 1
                issues_by_file[file_path] = issues_by_file.get(file_path, 0) + 1

        return {
            'issue_count': len(issue_lines),
            'issues_by_code': issues_by_code,
            'issues_by_file': issues_by_file
        }

