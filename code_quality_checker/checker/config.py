"""
Configuration Parser - 配置解析器

解析 .cqc.yaml 配置文件，支持 include/exclude 模式。
"""

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Optional, Dict, Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# 配置文件名
CONFIG_FILENAME = ".cqc.yaml"

# 默认排除模式
DEFAULT_EXCLUDE = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "*.egg-info",
    ".eggs",
}


@dataclass
class CheckerConfig:
    """检测配置"""
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    project_name: Optional[str] = None

    def should_include(self, path: Path, base: Path) -> bool:
        """
        判断路径是否应该被检测

        Args:
            path: 要检查的路径
            base: 项目根目录

        Returns:
            是否应该包含
        """
        try:
            rel_path = path.relative_to(base)
        except ValueError:
            rel_path = path

        rel_str = str(rel_path)

        # 检查是否在排除列表中
        for pattern in self.exclude:
            if self._match_pattern(rel_str, pattern):
                return False
            # 也检查路径的各个部分
            for part in rel_path.parts:
                if self._match_pattern(part, pattern):
                    return False

        # 如果没有 include 规则，默认包含所有
        if not self.include:
            return True

        # 检查是否在包含列表中
        for pattern in self.include:
            if self._match_pattern(rel_str, pattern):
                return True
            # 检查是否是 include 目录的子目录
            if rel_str.startswith(pattern.rstrip('/')):
                return True

        return False

    @staticmethod
    def _match_pattern(path_str: str, pattern: str) -> bool:
        """匹配 glob 模式"""
        # 处理目录模式 (结尾带 /)
        pattern = pattern.rstrip('/')

        # 直接匹配
        if fnmatch.fnmatch(path_str, pattern):
            return True

        # 尝试匹配路径的最后一部分
        path_name = Path(path_str).name
        if fnmatch.fnmatch(path_name, pattern):
            return True

        return False


def load_config(project_path: Path) -> CheckerConfig:
    """
    加载项目配置

    优先级：
    1. 项目目录下的 .cqc.yaml
    2. 默认配置（自动扫描）

    Args:
        project_path: 项目路径

    Returns:
        检测配置
    """
    config_file = project_path / CONFIG_FILENAME

    if config_file.exists():
        return _load_yaml_config(config_file)

    # 返回默认配置
    return CheckerConfig(
        include=[],  # 空表示自动扫描
        exclude=list(DEFAULT_EXCLUDE)
    )


def _load_yaml_config(config_file: Path) -> CheckerConfig:
    """加载 YAML 配置文件"""
    if not HAS_YAML:
        raise ImportError(
            "PyYAML is required to load .cqc.yaml config files. "
            "Install it with: pip install pyyaml"
        )

    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    include = data.get('include', [])
    exclude = data.get('exclude', [])
    project_name = data.get('name')

    # 合并默认排除
    all_exclude = list(DEFAULT_EXCLUDE)
    for pattern in exclude:
        if pattern not in all_exclude:
            all_exclude.append(pattern)

    return CheckerConfig(
        include=include if isinstance(include, list) else [include],
        exclude=all_exclude,
        project_name=project_name
    )


def find_targets(project_path: Path, config: CheckerConfig) -> List[Path]:
    """
    根据配置查找目标目录

    Args:
        project_path: 项目路径
        config: 检测配置

    Returns:
        目标目录列表
    """
    targets = []

    if config.include:
        # 使用 include 列表
        for pattern in config.include:
            # 处理 glob 模式
            if '*' in pattern:
                for match in project_path.glob(pattern):
                    if match.is_dir() and config.should_include(match, project_path):
                        targets.append(match)
            else:
                candidate = project_path / pattern.rstrip('/')
                if candidate.exists() and candidate.is_dir():
                    targets.append(candidate)
    else:
        # 自动扫描：查找包含 Python 文件的目录
        for item in project_path.iterdir():
            if not item.is_dir():
                continue
            if not config.should_include(item, project_path):
                continue
            # 检查是否包含 Python 文件
            if list(item.rglob("*.py")):
                targets.append(item)

    return targets

