# Changelog

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 环境变量配置支持,便于开源和多环境管理
- `.env.example` 环境变量模板文件
- 前端测试/生产环境配置
- 后端测试/生产环境配置(预留)
- MIT License 许可证
- 完善的 README 文档(项目背景、解决方案、适用场景)
- 贡献指南和开发规范
- Roadmap 规划

### Changed
- 配置管理从硬编码改为环境变量读取
- `.gitignore` 添加 `.env` 忽略规则

## [1.0.0] - 2025-11-12

### Added
- 云效 Pipeline 自动触发和构建监控
- 从构建日志提取镜像版本号
- K8s Deployment 镜像版本自动更新
- 登录状态管理 (`auth.json`)
- 失败时自动截图功能
- 详细日志输出
- 可配置的超时时间
- 无头/有头模式切换

### Core Modules
- `main.py` - 主程序入口
- `config.py` - 配置管理
- `yunxiao.py` - 云效操作模块
- `k8s.py` - K8s 操作模块
- `utils.py` - 工具函数

---

## 版本说明

- **[Unreleased]**: 未发布的变更
- **[1.0.0]**: 首个正式版本

---

更新日志格式:

### Added (新增)
新增的功能

### Changed (变更)
已有功能的变更

### Deprecated (弃用)
即将移除的功能

### Removed (移除)
已移除的功能

### Fixed (修复)
任何 bug 修复

### Security (安全)
安全相关的改进
