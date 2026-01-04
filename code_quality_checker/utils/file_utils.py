"""
File Utilities - 文件操作工具
"""

from pathlib import Path
from typing import List, Set, Optional


# 默认排除的目录
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    '.git', '__pycache__', '.venv', 'venv', 'env',
    'node_modules', 'outputs', 'build', 'dist',
    '.pytest_cache', '.mypy_cache', '.tox',
    'eggs', '*.egg-info', '.eggs'
}


def get_python_files(
    target_dirs: List[Path],
    exclude_patterns: Optional[Set[str]] = None
) -> List[Path]:
    """
    获取目标目录下所有 Python 文件

    Args:
        target_dirs: 目标目录列表
        exclude_patterns: 要排除的模式

    Returns:
        Python 文件路径列表
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_DIRS

    py_files: List[Path] = []

    for target_dir in target_dirs:
        if not target_dir.exists():
            continue

        for py_file in target_dir.rglob("*.py"):
            # 检查是否在排除目录中
            should_exclude = any(
                excluded in py_file.parts
                for excluded in exclude_patterns
            )
            if not should_exclude:
                py_files.append(py_file)

    return py_files


def find_directories(
    root: Path,
    patterns: Optional[List[str]] = None,
    exclude: Optional[Set[str]] = None
) -> List[Path]:
    """
    在根目录下查找匹配的子目录

    Args:
        root: 根目录
        patterns: 要匹配的目录名模式 (默认: 常见代码目录)
        exclude: 要排除的目录名

    Returns:
        匹配的目录列表
    """
    if patterns is None:
        patterns = [
            'tool', 'tools', 'scripts', 'src', 'lib',
            'unittest', 'tests', 'test',
            'core', 'modules', 'utils', 'app'
        ]

    if exclude is None:
        exclude = DEFAULT_EXCLUDE_DIRS

    found_dirs: List[Path] = []

    for pattern in patterns:
        dir_path = root / pattern
        if dir_path.exists() and dir_path.is_dir():
            found_dirs.append(dir_path)

    # 如果没找到标准目录，扫描所有包含 Python 文件的子目录
    if not found_dirs:
        for item in root.iterdir():
            if not item.is_dir():
                continue
            if item.name in exclude or item.name.startswith('.'):
                continue
            # 检查是否包含 Python 文件
            if list(item.rglob("*.py")):
                found_dirs.append(item)

    return found_dirs


def ensure_directory(path: Path) -> Path:
    """
    确保目录存在，不存在则创建

    Args:
        path: 目录路径

    Returns:
        目录路径
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

