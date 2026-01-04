#!/bin/bash
# ============================================
# Code Quality Checker - 远程部署脚本
# 使用 rsync 将工具包部署到远程机器
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_usage() {
    echo -e "${BLUE}Code Quality Checker - 远程部署工具${NC}"
    echo
    echo "用法: $0 [选项] <目标>"
    echo
    echo "目标格式:"
    echo "  user@host:/path/to/install    SSH 远程部署"
    echo "  /path/to/install              本地目录部署"
    echo
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -n, --dry-run       模拟运行 (不实际执行)"
    echo "  -v, --verbose       详细输出"
    echo "  -i, --install       部署后自动安装"
    echo "  --ssh-key <key>     指定 SSH 密钥"
    echo
    echo "示例:"
    echo "  $0 user@192.168.1.100:/home/user/tools"
    echo "  $0 /opt/code_quality_checker"
    echo "  $0 -i user@host:/home/user/tools"
    echo
}

# Default options
DRY_RUN=""
VERBOSE=""
AUTO_INSTALL=false
SSH_KEY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        -n|--dry-run)
            DRY_RUN="--dry-run"
            echo -e "${YELLOW}模拟运行模式${NC}"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -i|--install)
            AUTO_INSTALL=true
            shift
            ;;
        --ssh-key)
            SSH_KEY="-e 'ssh -i $2'"
            shift 2
            ;;
        -*)
            echo -e "${RED}错误: 未知选项 $1${NC}"
            print_usage
            exit 1
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

if [[ -z "$TARGET" ]]; then
    echo -e "${RED}错误: 请指定目标路径${NC}"
    print_usage
    exit 1
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Code Quality Checker - 部署${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# Exclude patterns
EXCLUDES=(
    "--exclude=.git"
    "--exclude=__pycache__"
    "--exclude=*.pyc"
    "--exclude=.venv"
    "--exclude=*.egg-info"
    "--exclude=reports"
    "--exclude=build"
    "--exclude=dist"
)

# Build rsync command
RSYNC_CMD="rsync -azh --progress ${DRY_RUN} ${VERBOSE} ${EXCLUDES[*]}"
if [[ -n "$SSH_KEY" ]]; then
    RSYNC_CMD="$RSYNC_CMD $SSH_KEY"
fi

# Determine if remote or local
if [[ "$TARGET" == *":"* ]]; then
    # Remote deployment
    REMOTE_HOST="${TARGET%%:*}"
    REMOTE_PATH="${TARGET#*:}"
    echo -e "${YELLOW}部署目标: ${REMOTE_HOST}:${REMOTE_PATH}${NC}"
    echo

    # Sync files
    echo -e "${BLUE}[1/2] 同步文件...${NC}"
    eval "$RSYNC_CMD ${SCRIPT_DIR}/ ${TARGET}/code_quality_checker/"

    if [[ "$AUTO_INSTALL" == true && -z "$DRY_RUN" ]]; then
        echo
        echo -e "${BLUE}[2/2] 远程安装...${NC}"
        ssh "${REMOTE_HOST}" "cd ${REMOTE_PATH}/code_quality_checker && pip install -e . -q"
        echo -e "${GREEN}✓ 远程安装完成${NC}"
    fi
else
    # Local deployment
    echo -e "${YELLOW}部署目标: ${TARGET}${NC}"
    echo

    # Create target directory if needed
    mkdir -p "${TARGET}"

    # Sync files
    echo -e "${BLUE}[1/2] 同步文件...${NC}"
    eval "$RSYNC_CMD ${SCRIPT_DIR}/ ${TARGET}/code_quality_checker/"

    if [[ "$AUTO_INSTALL" == true && -z "$DRY_RUN" ]]; then
        echo
        echo -e "${BLUE}[2/2] 本地安装...${NC}"
        cd "${TARGET}/code_quality_checker" && pip install -e . -q
        echo -e "${GREEN}✓ 安装完成${NC}"
    fi
fi

echo
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ 部署完成!${NC}"
echo -e "${GREEN}============================================${NC}"
echo

if [[ "$AUTO_INSTALL" == false ]]; then
    echo -e "${YELLOW}提示: 部署后请在目标机器上运行安装:${NC}"
    if [[ "$TARGET" == *":"* ]]; then
        echo -e "  ${BLUE}ssh ${REMOTE_HOST}${NC}"
        echo -e "  ${BLUE}cd ${REMOTE_PATH}/code_quality_checker${NC}"
    else
        echo -e "  ${BLUE}cd ${TARGET}/code_quality_checker${NC}"
    fi
    echo -e "  ${BLUE}./install.sh${NC}"
    echo
fi

