"""
Console Utilities - 控制台输出工具
"""

import sys


class Colors:
    """Terminal color codes"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'  # No Color

    @classmethod
    def disable(cls) -> None:
        """禁用颜色输出（用于非终端环境）"""
        cls.RED = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.BLUE = ''
        cls.MAGENTA = ''
        cls.CYAN = ''
        cls.WHITE = ''
        cls.GRAY = ''
        cls.NC = ''

    @classmethod
    def is_tty(cls) -> bool:
        """检查是否为终端环境"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def print_header(text: str, width: int = 70) -> None:
    """Print colored header"""
    print(f"{Colors.CYAN}{'=' * width}{Colors.NC}")
    print(f"{Colors.CYAN}{text:^{width}}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * width}{Colors.NC}\n")


def print_subheader(text: str, width: int = 70) -> None:
    """Print colored subheader"""
    print(f"{Colors.BLUE}{'─' * width}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'─' * width}{Colors.NC}\n")


def print_step(step_num: int, total: int, text: str) -> None:
    """Print step information"""
    print(f"{Colors.BLUE}[{step_num}/{total}] {text}{Colors.NC}")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}{text}{Colors.NC}\n")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}{text}{Colors.NC}\n")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}{text}{Colors.NC}\n")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.WHITE}{text}{Colors.NC}")


def print_dim(text: str) -> None:
    """Print dimmed/gray text"""
    print(f"{Colors.GRAY}{text}{Colors.NC}")

