"""
Orchestrator - 编排器

协调检测流程，生成报告。
"""

from pathlib import Path
from typing import List, Optional

from .base import Checker, CheckResult
from .config import CheckerConfig, load_config, DEFAULT_EXCLUDE
from ..utils import (
    print_header, print_step, print_success, print_warning, print_error,
    ReportGenerator, QualityMetrics
)


class Orchestrator:
    """
    编排器 - 协调检测流程

    负责:
    - 执行检测
    - 生成报告
    - 批量处理
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Args:
            output_dir: 报告输出目录
        """
        self.checker = Checker()
        self.output_dir = Path(output_dir) if output_dir else Path('reports')

    def check(
        self,
        project_path: Path,
        config: Optional[CheckerConfig] = None,
        verbose: bool = True
    ) -> CheckResult:
        """
        检测单个项目

        Args:
            project_path: 项目路径
            config: 可选的配置对象 (如果不提供，从项目目录加载 .cqc.yaml)
            verbose: 是否输出详细信息

        Returns:
            检测结果
        """
        project_path = Path(project_path).resolve()

        if verbose:
            print_header(f"Analyzing {project_path.name}")

        # 加载配置
        if config is None:
            config = load_config(project_path)

        if verbose:
            if config.include:
                print(f"Include: {config.include}")
            else:
                print("Include: (auto-scan)")
            custom_exclude = [e for e in config.exclude if e not in DEFAULT_EXCLUDE]
            if custom_exclude:
                print(f"Exclude: {custom_exclude}")
            print()

        # 执行检测
        result = self.checker.check(project_path, self.output_dir, config)

        if not result.success:
            if verbose:
                print_error(result.error_message)
            return result

        if verbose:
            print(f"Found directories: {[d.name for d in result.target_dirs]}")
            print(f"Found {result.python_files} Python files\n")

            # 输出各工具结果
            total = len(self.checker.tools)
            for i, tool in enumerate(self.checker.tools, 1):
                tool_result = result.tool_results.get(tool.name)
                if tool_result:
                    print_step(i, total, f"{tool.description}...")
                    if tool_result.success:
                        print_success(f"  → {tool_result.issue_count} issues")
                    else:
                        print_warning(f"  → Failed: {tool_result.error_message}")

        # 生成报告
        self._generate_report(result)

        if verbose:
            print_success(f"✅ Analysis complete")
            print(f"📁 Reports: {self.output_dir / result.project_name}")

        return result

    def batch_check(
        self,
        workspace: Path,
        config: Optional[CheckerConfig] = None,
        verbose: bool = True
    ) -> List[CheckResult]:
        """
        批量检测工作区中的所有项目

        为每个子目录项目生成独立报告，最后生成汇总报告。

        Args:
            workspace: 工作区路径
            config: 可选的共享配置 (如果不提供，各项目使用自己的 .cqc.yaml)
            verbose: 是否输出详细信息

        Returns:
            检测结果列表
        """
        workspace = Path(workspace).resolve()
        projects = self._find_projects(workspace)

        if not projects:
            if verbose:
                print_error("No projects found!")
            return []

        if verbose:
            print_header("Batch Code Quality Analysis")
            print(f"Found {len(projects)} projects:\n")
            for p in projects:
                print(f"  • {p.name}")
            print()

        results = []
        total = len(projects)

        for i, project in enumerate(projects, 1):
            if verbose:
                print(f"\n[{i}/{total}] {project.name}")

            # 使用共享配置或项目自己的配置
            project_config = config if config else load_config(project)
            result = self.checker.check(project, self.output_dir, project_config)
            results.append(result)

            if verbose:
                if result.success:
                    print_success(
                        f"  ✓ Files: {result.python_files} | "
                        f"Issues: {result.flake8_issues} | "
                        f"Duplicates: {result.duplicate_blocks} | "
                        f"Complex: {result.high_complexity}"
                    )
                else:
                    print_warning(f"  ✗ {result.error_message}")

            # 生成单项目报告
            if result.success:
                self._generate_report(result)

        # 生成批量汇总报告
        self._generate_batch_report(results)

        if verbose:
            print_header("Batch Analysis Complete")
            successful = sum(1 for r in results if r.success)
            print(f"📊 Analyzed: {successful}/{len(results)} projects")
            print(f"📁 Reports: {self.output_dir}")
            print(f"📄 Summary: {self.output_dir / 'SUMMARY.md'}")

        return results

    def _find_projects(self, workspace: Path) -> List[Path]:
        """查找工作区中的项目"""
        projects = []

        for item in workspace.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith('.'):
                continue
            if item.name in {'node_modules', '__pycache__', 'venv', '.venv', 'env'}:
                continue

            # 检查是否包含 Python 文件或配置文件
            has_config = (item / '.cqc.yaml').exists()
            has_python = bool(list(item.rglob("*.py")))

            if has_config or has_python:
                projects.append(item)

        return sorted(projects, key=lambda x: x.name)

    def _generate_report(self, result: CheckResult) -> None:
        """生成单项目报告"""
        if not result.success:
            return

        metrics = QualityMetrics(
            flake8_issues=result.flake8_issues,
            duplicate_blocks=result.duplicate_blocks,
            high_complexity=result.high_complexity,
            python_files=result.python_files,
            project_name=result.project_name
        )

        summary_path = self.output_dir / result.project_name / "SUMMARY.md"
        ReportGenerator.generate_summary_markdown(metrics, summary_path)

    def _generate_batch_report(self, results: List[CheckResult]) -> None:
        """生成批量汇总报告"""
        successful = [r for r in results if r.success]
        if not successful:
            return

        metrics_list = [
            QualityMetrics(
                flake8_issues=r.flake8_issues,
                duplicate_blocks=r.duplicate_blocks,
                high_complexity=r.high_complexity,
                python_files=r.python_files,
                project_name=r.project_name
            )
            for r in successful
        ]

        summary_path = self.output_dir / "SUMMARY.md"
        ReportGenerator.generate_batch_summary(metrics_list, summary_path)
