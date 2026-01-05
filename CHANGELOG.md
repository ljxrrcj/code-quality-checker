# Changelog

## [Unreleased] - 2026-01-05

### Added
- **空白字符自动清理功能**: 新增 `--cb` (clean blank) 选项
  - 自动修复 W293: 空行包含空白字符
  - 自动修复 W391: 文件末尾多余的空行
  - 自动修复 W291: 行尾空白字符
- 新增 `cleaners` 模块
  - `WhitespaceCleaner` 类：提供空白字符清理功能
  - 支持单文件和目录批量清理
  - 提供详细的清理报告和统计

### Changed
- 更新 CLI 帮助信息，添加 `--cb` 选项说明
- 更新 README 文档，添加自动修复功能使用说明

### Usage
```bash
# 检测项目代码质量
cqc /path/to/project

# 自动修复空白字符问题
cqc --cb /path/to/project

# 静默模式修复
cqc --cb -q /path/to/project
```

---

## [1.0.0] - 2026-01-04

### Initial Release
- 基础代码质量检测功能
- 集成 flake8, pylint, radon
- 支持批量检测模式
- 生成详细的质量报告
- 支持配置文件驱动

