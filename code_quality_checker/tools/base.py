"""
Base Tool - 工具基类

所有检测工具的抽象基类，定义统一接口。
"""

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_name: str
    success: bool
    issue_count: int = 0
    raw_output: str = ""
    report_file: Optional[Path] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""

    def __bool__(self) -> bool:
        return self.success


class BaseTool(ABC):
    """
    检测工具基类

    子类需要实现:
    - name: 工具名称
    - run(): 执行检测
    - parse_output(): 解析输出
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Args:
            config_path: 可选的配置文件路径
        """
        self.config_path = config_path

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    def description(self) -> str:
        """工具描述"""
        return f"{self.name} code quality tool"

    @abstractmethod
    def build_command(self, targets: List[Path]) -> str:
        """
        构建执行命令

        Args:
            targets: 目标文件或目录列表

        Returns:
            命令字符串
        """
        pass

    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        解析工具输出

        Args:
            output: 工具原始输出

        Returns:
            解析后的结果字典
        """
        pass

    def run(
        self,
        targets: List[Path],
        output_file: Optional[Path] = None
    ) -> ToolResult:
        """
        执行检测

        Args:
            targets: 目标文件或目录列表
            output_file: 可选的输出文件路径

        Returns:
            ToolResult 结果对象
        """
        if not targets:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_message="No targets specified"
            )

        cmd = self.build_command(targets)

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False  # 不抛出异常，因为检测工具返回非零通常表示有问题
            )

            output = result.stdout
            if result.stderr:
                output += f"\n=== STDERR ===\n{result.stderr}"

            # 保存到文件
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)

            # 解析输出
            parsed = self.parse_output(result.stdout)

            return ToolResult(
                tool_name=self.name,
                success=True,
                issue_count=parsed.get('issue_count', 0),
                raw_output=output,
                report_file=output_file,
                details=parsed
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error_message=str(e)
            )

    def check_available(self) -> bool:
        """检查工具是否可用"""
        try:
            subprocess.run(
                f"{self.name} --version",
                shell=True,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

