# 🔍 Code Quality Checker

Python 代码质量检测工具 - 配置文件驱动，极简接口

## 🚀 快速开始

```bash
# 安装
pip install -e /path/to/code_quality_checker

# 检测项目
cqc /path/to/project

# 批量检测
cqc -b /path/to/workspace

# 自动修复空白字符问题
cqc --cb /path/to/project
```

## 📋 命令行参数

```
cqc [选项] <路径>

选项:
  -b, --batch         批量检测模式 (为每个子目录生成独立报告)
  -c, --config FILE   指定配置文件路径 (默认: 项目目录下的 .cqc.yaml)
  -o, --output DIR    输出目录 (默认: reports)
  -q, --quiet         静默模式
  --cb, --clean-blank 自动清理空白字符问题 (W293, W391, W291)
  -v, --version       显示版本

示例:
  cqc /path/to/project                检测项目
  cqc -o reports /path/to/project     指定输出目录
  cqc -c my.yaml /path/to/project     使用指定配置文件
  cqc -b /path/to/workspace           批量检测工作区
  cqc --cb /path/to/project           自动修复空白字符问题
```

## 📝 配置文件

在项目根目录创建 `.cqc.yaml`：

```yaml
include:
  - src/
  - lib/
  - tests/

exclude:
  - vendor/
  - "**/migrations/"
  - build/

# 可选
name: my-project
```

### 配置示例

**Agent 项目:**
```yaml
include:
  - tool/
  - unittest/

exclude:
  - drivers_lib/
  - configs/
  - outputs/
```

**Django 项目:**
```yaml
include:
  - apps/
  - core/
  - api/

exclude:
  - "**/migrations/"
  - static/
```

### 无配置模式

如果没有 `.cqc.yaml`，工具会：
1. 自动扫描包含 Python 文件的目录
2. 排除常见非代码目录 (venv, __pycache__, node_modules 等)

## 📊 输出报告

### 单项目模式
```
reports/
└── my-project/
    ├── SUMMARY.md           # 汇总报告
    ├── flake8_report.txt    # 代码风格
    ├── pylint_report.txt    # 代码质量
    ├── radon_cc_report.txt  # 复杂度
    └── radon_mi_report.txt  # 可维护性
```

### 批量模式 (-b)
```
reports/
├── project-a/
│   ├── SUMMARY.md
│   └── ...
├── project-b/
│   ├── SUMMARY.md
│   └── ...
└── SUMMARY.md               # 批量汇总报告
```

## 🧹 自动修复功能

`--cb` (clean blank) 选项可以自动修复以下空白字符问题：

- **W293**: 空行包含空白字符
- **W391**: 文件末尾多余的空行
- **W291**: 行尾空白字符

```bash
# 修复单个文件
cqc --cb /path/to/file.py

# 修复整个项目
cqc --cb /path/to/project

# 静默模式修复
cqc --cb -q /path/to/project
```

**修复内容**：
- 清理空行中的空白字符
- 删除行尾的空白字符
- 确保文件以单个换行符结束

## 🔧 Python API

```python
from code_quality_checker import Orchestrator
from code_quality_checker.cleaners import WhitespaceCleaner

# 代码质量检测
orchestrator = Orchestrator(output_dir='reports')
result = orchestrator.check('/path/to/project')
print(f"Issues: {result.flake8_issues}")

# 批量检测
results = orchestrator.batch_check('/path/to/workspace')

# 空白字符清理
cleaner = WhitespaceCleaner(verbose=True)
cleaner.clean_directory('/path/to/project')
print(cleaner.get_summary())
```

## 📄 License

MIT License
