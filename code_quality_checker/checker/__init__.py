"""
Checker - 代码质量检测

基于配置文件 (.cqc.yaml) 驱动的统一检测器。

使用方式:
    from code_quality_checker.checker import Orchestrator

    # 检测单个项目
    orchestrator = Orchestrator(output_dir='reports')
    result = orchestrator.check('/path/to/project')

    # 批量检测
    results = orchestrator.batch('/path/to/workspace')
"""

from .base import Checker, CheckResult
from .config import CheckerConfig, load_config, find_targets
from .orchestrator import Orchestrator

__all__ = [
    "Checker",
    "CheckResult",
    "CheckerConfig",
    "load_config",
    "find_targets",
    "Orchestrator",
]
