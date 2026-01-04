#!/bin/bash
# ============================================
# Code Quality Checker - 安装脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Code Quality Checker - 安装程序${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# Check Python version
echo -e "${YELLOW}[1/5] 检查 Python 版本...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} 已安装${NC}"
else
    echo -e "${RED}✗ Python 3 未找到，请先安装 Python 3.8+${NC}"
    exit 1
fi

# Create virtual environment (optional)
echo
echo -e "${YELLOW}[2/5] 创建虚拟环境 (可选)...${NC}"
read -p "是否创建独立虚拟环境? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    echo -e "${GREEN}✓ 虚拟环境已创建: ${VENV_DIR}${NC}"
else
    echo -e "${YELLOW}跳过虚拟环境创建${NC}"
fi

# Upgrade pip
echo
echo -e "${YELLOW}[3/5] 升级 pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ pip 已更新${NC}"

# Install dependencies
echo
echo -e "${YELLOW}[4/5] 安装依赖...${NC}"
pip install -r "${SCRIPT_DIR}/requirements.txt" -q
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# Install package
echo
echo -e "${YELLOW}[5/5] 安装 code-quality-checker...${NC}"
pip install -e "${SCRIPT_DIR}" -q
echo -e "${GREEN}✓ 安装完成${NC}"

# Verify installation
echo
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ 安装成功!${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo -e "可用命令:"
echo -e "  ${YELLOW}cqc${NC}        - 主命令入口"
echo -e "  ${YELLOW}cqc-check${NC}  - 检查单个项目"
echo -e "  ${YELLOW}cqc-batch${NC}  - 批量检查项目"
echo
echo -e "快速开始:"
echo -e "  ${BLUE}cqc check my_project /path/to/project${NC}"
echo -e "  ${BLUE}cqc batch --workspace /path/to/workspace${NC}"
echo
echo -e "获取帮助:"
echo -e "  ${BLUE}cqc --help${NC}"
echo

if [[ -d "${VENV_DIR}" ]]; then
    echo -e "${YELLOW}提示: 使用前请激活虚拟环境:${NC}"
    echo -e "  ${BLUE}source ${VENV_DIR}/bin/activate${NC}"
    echo
fi

