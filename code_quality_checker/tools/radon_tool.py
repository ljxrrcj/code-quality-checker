"""
Radon Tools - 复杂度分析工具封装
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import BaseTool


class RadonCCTool(BaseTool):
    """
    Radon Cyclomatic Complexity - 圈复杂度分析工具

    复杂度等级:
    - A (1-5): 简单
    - B (6-10): 较复杂
    - C (11-20): 复杂
    - D (21-30): 非常复杂
    - E (31-40): 极度复杂
    - F (41+): 不可维护
    """

    @property
    def name(self) -> str:
        return "radon_cc"

    @property
    def description(self) -> str:
        return "圈复杂度分析 (Cyclomatic Complexity)"

    def build_command(self, targets: List[Path]) -> str:
        targets_str = " ".join(str(t) for t in targets)
        return f"radon cc {targets_str} -a -s"

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        解析 Radon CC 输出

        Returns:
            {
                'issue_count': int,  # 高复杂度函数数
                'functions_by_grade': {'A': 50, 'B': 20, 'C': 5, ...},
                'high_complexity_functions': [{'name': ..., 'grade': ..., 'score': ...}]
            }
        """
        functions_by_grade: Dict[str, int] = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0
        }
        high_complexity_functions: List[Dict[str, Any]] = []

        # 匹配函数行: "    M 45:4 some_method - C (15)"
        pattern = re.compile(r'\s+[MFC]\s+\d+:\d+\s+(\w+)\s+-\s+([A-F])\s+\((\d+)\)')

        for line in output.split('\n'):
            match = pattern.search(line)
            if match:
                func_name = match.group(1)
                grade = match.group(2)
                score = int(match.group(3))

                functions_by_grade[grade] = functions_by_grade.get(grade, 0) + 1

                # 收集高复杂度函数 (C 及以上)
                if grade in ('C', 'D', 'E', 'F'):
                    high_complexity_functions.append({
                        'name': func_name,
                        'grade': grade,
                        'score': score,
                        'line': line.strip()
                    })

        # 高复杂度函数数 (C, D, E, F)
        high_count = sum(
            functions_by_grade.get(g, 0)
            for g in ('C', 'D', 'E', 'F')
        )

        return {
            'issue_count': high_count,
            'functions_by_grade': functions_by_grade,
            'high_complexity_functions': high_complexity_functions
        }


class RadonMITool(BaseTool):
    """
    Radon Maintainability Index - 可维护性指数分析工具

    可维护性等级:
    - A (100-20): 高可维护性
    - B (19-10): 中等可维护性
    - C (9-0): 低可维护性
    """

    @property
    def name(self) -> str:
        return "radon_mi"

    @property
    def description(self) -> str:
        return "可维护性指数分析 (Maintainability Index)"

    def build_command(self, targets: List[Path]) -> str:
        targets_str = " ".join(str(t) for t in targets)
        return f"radon mi {targets_str} -s"

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        解析 Radon MI 输出

        Returns:
            {
                'issue_count': int,  # 低可维护性文件数
                'files_by_grade': {'A': 40, 'B': 8, 'C': 2},
                'low_maintainability_files': [{'file': ..., 'grade': ..., 'score': ...}]
            }
        """
        files_by_grade: Dict[str, int] = {'A': 0, 'B': 0, 'C': 0}
        low_maintainability_files: List[Dict[str, Any]] = []

        # 匹配文件行: "path/to/file.py - A (85.5)"
        pattern = re.compile(r'(.+\.py)\s+-\s+([ABC])\s+\(([\d.]+)\)')

        for line in output.split('\n'):
            match = pattern.search(line)
            if match:
                file_path = match.group(1).strip()
                grade = match.group(2)
                score = float(match.group(3))

                files_by_grade[grade] = files_by_grade.get(grade, 0) + 1

                # 收集低可维护性文件 (B 及以下)
                if grade in ('B', 'C'):
                    low_maintainability_files.append({
                        'file': file_path,
                        'grade': grade,
                        'score': score
                    })

        # 低可维护性文件数 (C 级)
        low_count = files_by_grade.get('C', 0)

        return {
            'issue_count': low_count,
            'files_by_grade': files_by_grade,
            'low_maintainability_files': low_maintainability_files
        }

