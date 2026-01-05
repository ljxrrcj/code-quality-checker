#!/usr/bin/env python3
"""
空白字符清理器

自动修复以下代码风格问题：
- W293: 空行包含空白字符
- W391: 文件末尾空行
- W291: 行尾空白字符
"""

from pathlib import Path
from typing import Optional


class CleanResult:
    """清理结果"""

    def __init__(self, filepath: Path, modified: bool, message: str) -> None:
        self.filepath = filepath
        self.modified = modified
        self.message = message


class WhitespaceCleaner:
    """空白字符清理器"""

    def __init__(self, verbose: bool = True) -> None:
        """
        初始化清理器。

        Args:
            verbose: 是否输出详细信息
        """
        self.verbose = verbose
        self.fixed_count = 0
        self.total_count = 0

    def clean_file(self, filepath: Path) -> CleanResult:
        """
        清理单个文件的空白字符问题。

        Args:
            filepath: 文件路径

        Returns:
            CleanResult: 清理结果
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content
            lines = content.splitlines(keepends=True)

            # 修复 W293: 空行包含空白字符
            # 修复 W291: 行尾空白字符
            fixed_lines = []
            for line in lines:
                # 如果是空行（只包含空白字符），清空它
                if line.strip() == '':
                    fixed_lines.append('\n' if line.endswith('\n') else '')
                else:
                    # 去除行尾空白字符，但保留换行符
                    fixed_lines.append(
                        line.rstrip() + ('\n' if line.endswith('\n') else '')
                    )

            content = ''.join(fixed_lines)

            # 修复 W391: 文件末尾空行
            # 确保文件以单个换行符结束，不要有多余的空行
            content = content.rstrip() + '\n'

            if content != original_content:
                filepath.write_text(content, encoding='utf-8')
                self.fixed_count += 1
                return CleanResult(filepath, True, "✓ 已修复")
            else:
                return CleanResult(filepath, False, "○ 无需修改")

        except Exception as e:
            return CleanResult(filepath, False, f"✗ 错误: {e}")

    def clean_directory(
        self,
        directory: Path,
        pattern: str = "*.py",
        recursive: bool = True,
    ) -> list[CleanResult]:
        """
        清理目录中的所有文件。

        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            recursive: 是否递归处理子目录

        Returns:
            list[CleanResult]: 所有文件的清理结果
        """
        results = []

        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))

        self.total_count = len(files)
        self.fixed_count = 0

        for file_path in files:
            if not file_path.is_file():
                continue

            result = self.clean_file(file_path)
            results.append(result)

            if self.verbose:
                print(f"{result.message}: {result.filepath}")

        return results

    def get_summary(self) -> str:
        """
        获取清理摘要。

        Returns:
            str: 摘要信息
        """
        return f"总结: 修复了 {self.fixed_count}/{self.total_count} 个文件"


def clean_whitespace(
    path: Path,
    pattern: str = "*.py",
    recursive: bool = True,
    verbose: bool = True,
) -> tuple[int, int]:
    """
    便捷函数：清理空白字符。

    Args:
        path: 文件或目录路径
        pattern: 文件匹配模式（仅目录时有效）
        recursive: 是否递归处理子目录
        verbose: 是否输出详细信息

    Returns:
        tuple[int, int]: (修复的文件数, 总文件数)
    """
    cleaner = WhitespaceCleaner(verbose=verbose)

    if path.is_file():
        result = cleaner.clean_file(path)
        if verbose:
            print(f"{result.message}: {result.filepath}")
        return (1 if result.modified else 0, 1)

    elif path.is_dir():
        results = cleaner.clean_directory(path, pattern, recursive)
        if verbose:
            print(f"\n{cleaner.get_summary()}")
        return (cleaner.fixed_count, cleaner.total_count)

    else:
        raise ValueError(f"路径不存在: {path}")

