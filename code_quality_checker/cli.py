#!/usr/bin/env python3
"""
Code Quality Checker - CLI

极简命令行入口，配置通过 .cqc.yaml 文件驱动。
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .checker import Orchestrator
from .checker.config import CheckerConfig, DEFAULT_EXCLUDE
from .cleaners import WhitespaceCleaner
from .utils import Colors


def main() -> int:
    """CLI 入口"""
    args = _parse_args()

    if not args.path:
        return 0  # argparse 已经打印了帮助

    path = _validate_path(args.path)
    if path is None:
        return 1

    # cb (clean blank) 模式：清理空白字符
    if args.clean_blank:
        return _run_clean_blank(path, args)

    config = _load_config(args.config)
    if config is False:  # 配置加载失败
        return 1

    return _run(path, config, args)


def _parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog='cqc',
        description='Code Quality Checker - Python 代码质量检测',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式:
  cqc /path/to/project                检测项目
  cqc -o reports /path/to/project     指定输出目录
  cqc -c my.yaml /path/to/project     指定配置文件
  cqc -b /path/to/workspace           批量检测
  cqc --cb /path/to/project           清理空白字符问题
        """
    )

    parser.add_argument('-b', '--batch', action='store_true',
                        help='批量检测模式')
    parser.add_argument('-c', '--config', metavar='FILE',
                        help='指定配置文件路径')
    parser.add_argument('-o', '--output', default='reports',
                        help='输出目录 (默认: reports)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式')
    parser.add_argument('--cb', '--clean-blank', dest='clean_blank',
                        action='store_true',
                        help='清理空白字符问题 (W293, W391, W291)')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}')
    parser.add_argument('path', nargs='?',
                        help='项目路径或工作区路径')

    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        print(f"\n{Colors.YELLOW}示例: cqc /path/to/project{Colors.NC}")

    return args


def _validate_path(path_str: str) -> Optional[Path]:
    """验证路径存在"""
    path = Path(path_str).resolve()
    if not path.exists():
        print(f"{Colors.RED}错误: 路径不存在 {path}{Colors.NC}")
        return None
    return path


def _load_config(config_path: Optional[str]) -> Optional[CheckerConfig]:
    """
    加载配置文件

    Returns:
        CheckerConfig: 成功
        None: 未指定配置
        False: 加载失败
    """
    if not config_path:
        return None

    path = Path(config_path)
    if not path.exists():
        print(f"{Colors.RED}错误: 配置文件不存在 {path}{Colors.NC}")
        return False

    try:
        import yaml
    except ImportError:
        print(f"{Colors.RED}错误: 需要 pyyaml 来解析配置文件{Colors.NC}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    include = data.get('include', [])
    exclude = data.get('exclude', [])

    all_exclude = list(DEFAULT_EXCLUDE)
    for pattern in exclude:
        if pattern not in all_exclude:
            all_exclude.append(pattern)

    return CheckerConfig(
        include=include if isinstance(include, list) else [include],
        exclude=all_exclude,
        project_name=data.get('name')
    )


def _run(path: Path, config: Optional[CheckerConfig], args) -> int:
    """执行检测"""
    orchestrator = Orchestrator(output_dir=Path(args.output))
    verbose = not args.quiet

    if args.batch:
        results = orchestrator.batch_check(path, config=config, verbose=verbose)
        return 0 if any(r.success for r in results) else 1

    result = orchestrator.check(path, config=config, verbose=verbose)
    return 0 if result.success else 1


def _run_clean_blank(path: Path, args) -> int:
    """执行空白字符清理"""
    verbose = not args.quiet

    if verbose:
        print(f"{Colors.BLUE}🧹 开始清理空白字符...{Colors.NC}\n")

    try:
        cleaner = WhitespaceCleaner(verbose=verbose)

        if path.is_file():
            result = cleaner.clean_file(path)
            if verbose:
                print(f"{result.message}: {result.filepath}")
            success = result.modified
        else:
            cleaner.clean_directory(path, pattern="*.py", recursive=True)
            if verbose:
                print(f"\n{cleaner.get_summary()}")
            success = cleaner.fixed_count > 0

        if verbose:
            if success:
                print(f"\n{Colors.GREEN}✓ 清理完成！{Colors.NC}")
            else:
                print(f"\n{Colors.YELLOW}○ 没有需要修复的文件{Colors.NC}")

        return 0

    except Exception as e:
        print(f"{Colors.RED}错误: {e}{Colors.NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
