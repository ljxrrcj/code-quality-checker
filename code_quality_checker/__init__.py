"""
Code Quality Checker - Python 代码质量检测工具包

基于配置文件 (.cqc.yaml) 驱动的代码质量检测。

快速开始:
    # 命令行
    cqc /path/to/project

    # Python API
    from code_quality_checker import Orchestrator

    orchestrator = Orchestrator(output_dir='reports')
    result = orchestrator.check('/path/to/project')

配置文件 (.cqc.yaml):
    include:
      - src/
      - tests/

    exclude:
      - vendor/
      - "**/migrations/"
"""

__version__ = "1.0.0"
__author__ = "KaiHong DevOps Team"

# 核心组件
from .checker import Orchestrator, Checker, CheckResult, CheckerConfig
from .tools import Flake8Tool, PylintTool, RadonCCTool, RadonMITool
from .utils import Colors, ReportGenerator, QualityMetrics

__all__ = [
    "__version__",
    # Checker
    "Orchestrator",
    "Checker",
    "CheckResult",
    "CheckerConfig",
    # Tools
    "Flake8Tool",
    "PylintTool",
    "RadonCCTool",
    "RadonMITool",
    # Utils
    "Colors",
    "ReportGenerator",
    "QualityMetrics",
]
