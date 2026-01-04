"""
Checker - 代码质量检测器

基于配置文件 (.cqc.yaml) 的统一检测器。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional

from .config import CheckerConfig, load_config, find_targets
from ..tools import BaseTool, ToolResult, Flake8Tool, PylintTool, RadonCCTool, RadonMITool
from ..utils import get_python_files


@dataclass
class CheckResult:
    """检测结果"""
    project_name: str
    project_path: Path
    success: bool = True
    python_files: int = 0
    target_dirs: List[Path] = field(default_factory=list)
    tool_results: Dict[str, ToolResult] = field(default_factory=dict)
    error_message: str = ""

    @property
    def flake8_issues(self) -> int:
        result = self.tool_results.get('flake8')
        return result.issue_count if result else 0

    @property
    def duplicate_blocks(self) -> int:
        result = self.tool_results.get('pylint')
        return result.details.get('duplicate_blocks', 0) if result else 0

    @property
    def high_complexity(self) -> int:
        result = self.tool_results.get('radon_cc')
        return result.issue_count if result else 0


class Checker:
    """
    代码质量检测器

    基于 .cqc.yaml 配置文件驱动。
    """

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """
        Args:
            tools: 检测工具列表，默认使用全部工具
        """
        self.tools = tools or [
            Flake8Tool(),
            PylintTool(),
            RadonCCTool(),
            RadonMITool()
        ]

    def check(
        self,
        project_path: Path,
        output_dir: Optional[Path] = None,
        config: Optional[CheckerConfig] = None
    ) -> CheckResult:
        """
        检测项目

        Args:
            project_path: 项目路径
            output_dir: 报告输出目录
            config: 可选的配置对象（如果不提供，从项目目录加载）

        Returns:
            检测结果
        """
        project_path = Path(project_path).resolve()
        project_name = project_path.name

        if not project_path.exists():
            return CheckResult(
                project_name=project_name,
                project_path=project_path,
                success=False,
                error_message=f"Project path does not exist: {project_path}"
            )

        # 加载配置
        if config is None:
            config = load_config(project_path)

        if config.project_name:
            project_name = config.project_name

        # 查找目标目录
        target_dirs = find_targets(project_path, config)
        if not target_dirs:
            return CheckResult(
                project_name=project_name,
                project_path=project_path,
                success=False,
                error_message="No target directories found"
            )

        # 过滤 Python 文件
        py_files = self._get_python_files(target_dirs, config, project_path)
        if not py_files:
            return CheckResult(
                project_name=project_name,
                project_path=project_path,
                success=False,
                error_message="No Python files found"
            )

        # 运行工具
        report_dir = output_dir / project_name if output_dir else None
        tool_results = self._run_tools(target_dirs, report_dir)

        return CheckResult(
            project_name=project_name,
            project_path=project_path,
            success=True,
            python_files=len(py_files),
            target_dirs=target_dirs,
            tool_results=tool_results
        )

    def _get_python_files(
        self,
        target_dirs: List[Path],
        config: CheckerConfig,
        project_path: Path
    ) -> List[Path]:
        """获取过滤后的 Python 文件列表"""
        all_files = get_python_files(target_dirs)
        return [
            f for f in all_files
            if config.should_include(f, project_path)
        ]

    def _run_tools(
        self,
        targets: List[Path],
        output_dir: Optional[Path]
    ) -> Dict[str, ToolResult]:
        """运行所有检测工具"""
        results = {}

        for tool in self.tools:
            output_file = None
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{tool.name}_report.txt"

            result = tool.run(targets, output_file)
            results[tool.name] = result

        return results
