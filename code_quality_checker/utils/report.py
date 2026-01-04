"""
Report Generator - 报告生成工具
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class QualityMetrics:
    """代码质量指标"""
    flake8_issues: int = 0
    duplicate_blocks: int = 0
    high_complexity: int = 0
    python_files: int = 0
    project_name: str = ""

    @property
    def score(self) -> float:
        """计算总分 (100分制)"""
        total_score = 100.0
        total_score -= min(self.flake8_issues * 0.2, 30)
        total_score -= min(self.duplicate_blocks * 1.5, 40)
        total_score -= min(self.high_complexity * 2, 30)
        return max(0, total_score)

    @property
    def rating(self) -> str:
        """获取评级"""
        score = self.score
        if score >= 80:
            return "优秀"
        if score >= 60:
            return "良好"
        if score >= 40:
            return "中等"
        return "较差"

    @property
    def rating_emoji(self) -> str:
        """获取评级图标"""
        score = self.score
        if score >= 80:
            return "✅"
        if score >= 60:
            return "⚠️"
        if score >= 40:
            return "🔶"
        return "🔴"


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def get_level_indicator(value: int, thresholds: tuple) -> str:
        """
        根据阈值获取等级指示器

        Args:
            value: 数值
            thresholds: (低阈值, 高阈值)

        Returns:
            等级字符串
        """
        low, high = thresholds
        if value < low:
            return "🟢 低"
        if value < high:
            return "🟡 中"
        return "🔴 高"

    @staticmethod
    def generate_summary_markdown(
        metrics: QualityMetrics,
        output_path: Path,
        extra_info: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        生成 Markdown 格式的汇总报告

        Args:
            metrics: 质量指标
            output_path: 输出路径
            extra_info: 额外信息

        Returns:
            报告文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 代码质量分析报告 - {metrics.project_name}\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Python 文件数**: {metrics.python_files}\n\n")
            f.write("---\n\n")

            # 问题统计表
            f.write("## 📊 问题统计\n\n")
            f.write("| 类型 | 数量 | 等级 |\n")
            f.write("|------|------|------|\n")

            flake8_level = ReportGenerator.get_level_indicator(
                metrics.flake8_issues, (50, 200)
            )
            f.write(f"| 代码风格问题 | {metrics.flake8_issues} | {flake8_level} |\n")

            dup_level = ReportGenerator.get_level_indicator(
                metrics.duplicate_blocks, (10, 30)
            )
            f.write(f"| 重复代码块 | {metrics.duplicate_blocks} | {dup_level} |\n")

            complex_level = ReportGenerator.get_level_indicator(
                metrics.high_complexity, (5, 15)
            )
            f.write(f"| 高复杂度函数 | {metrics.high_complexity} | {complex_level} |\n")

            # 详细报告
            f.write("\n---\n\n")
            f.write("## 📁 详细报告\n\n")
            f.write("- `flake8_report.txt` - 代码风格详细问题\n")
            f.write("- `pylint_report.txt` - 代码质量和重复检测\n")
            f.write("- `radon_cc_report.txt` - 复杂度分析\n")
            f.write("- `radon_mi_report.txt` - 可维护性指数\n")

            # 评分
            f.write("\n---\n\n")
            f.write("## 📈 代码质量评分\n\n")
            f.write(f"**总分**: {metrics.score:.1f}/100\n\n")
            f.write(f"{metrics.rating_emoji} **评级**: {metrics.rating}\n")

            # 额外信息
            if extra_info:
                f.write("\n---\n\n")
                f.write("## 📋 额外信息\n\n")
                for key, value in extra_info.items():
                    f.write(f"- **{key}**: {value}\n")

        return output_path

    @staticmethod
    def generate_batch_summary(
        all_metrics: List[QualityMetrics],
        output_path: Path
    ) -> Path:
        """
        生成批量检查汇总报告

        Args:
            all_metrics: 所有项目的质量指标
            output_path: 输出路径

        Returns:
            报告文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🔍 代码质量批量分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**分析项目数**: {len(all_metrics)}\n\n")
            f.write("---\n\n")

            # 整体统计
            total_files = sum(m.python_files for m in all_metrics)
            total_flake8 = sum(m.flake8_issues for m in all_metrics)
            total_dup = sum(m.duplicate_blocks for m in all_metrics)
            total_complex = sum(m.high_complexity for m in all_metrics)

            f.write("## 📊 整体统计\n\n")
            f.write("| 指标 | 总数 |\n")
            f.write("|------|------|\n")
            f.write(f"| Python 文件总数 | {total_files} |\n")
            f.write(f"| 代码风格问题 | {total_flake8} |\n")
            f.write(f"| 重复代码块 | {total_dup} |\n")
            f.write(f"| 高复杂度函数 | {total_complex} |\n")

            # 各项目结果
            f.write("\n---\n\n")
            f.write("## 📋 各项目详细结果\n\n")
            f.write("| 项目 | 文件数 | 风格问题 | 重复代码 | 高复杂度 | 评分 | 评级 |\n")
            f.write("|------|--------|---------|---------|---------|------|------|\n")

            for m in sorted(all_metrics, key=lambda x: x.score):
                f.write(
                    f"| {m.project_name} | {m.python_files} | "
                    f"{m.flake8_issues} | {m.duplicate_blocks} | "
                    f"{m.high_complexity} | {m.score:.1f} | "
                    f"{m.rating_emoji} {m.rating} |\n"
                )

            f.write("\n---\n\n")
            f.write("*报告由 Code Quality Checker 自动生成*\n")

        return output_path

