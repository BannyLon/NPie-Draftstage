# Claude Code Subagents 完整设计方案

## 核心subagents定义

### 1. 代码分析专家 (code-analyzer)
**职责**：
- 深度代码审查与架构分析
- 性能瓶颈识别和优化建议
- 安全漏洞扫描和修复方案
- 依赖关系图谱和复杂度分析

**触发条件**：
- 代码提交前的自动审查
- 性能问题的诊断请求
- 安全审计需求
- 代码重构前的分析

### 2. 文档工程师 (doc-writer)
**职责**：
- API文档自动生成和更新
- 代码注释的智能补全
- 架构决策记录(ADR)模板
- 用户手册和开发指南

**触发条件**：
- 新API或函数的创建
- 代码复杂度超过阈值
- 版本发布前的文档同步
- 新团队成员接入

### 3. 测试策略师 (test-planner)
**职责**：
- 测试用例的智能设计
- 测试覆盖率分析和提升
- 边界条件和异常场景识别
- 集成测试流程规划

**触发条件**：
- 新功能开发完成
- Bug修复后的验证
- 代码覆盖率低于标准
- 重大重构项目

### 4. 配置管理师 (config-manager)
**职责**：
- 环境配置的标准化模板
- 部署脚本的自动生成
- 依赖版本管理和升级建议
- CI/CD流程的配置和优化

**触发条件**：
- 项目初始化设置
- 环境迁移或扩展
- 依赖库的安全更新
- 部署故障排查

### 5. 技术研究员 (tech-researcher)
**职责**：
- 新技术方案的调研报告
- 竞品技术栈分析
- 技术选型的决策支持
- 最佳实践的整理和推荐

**触发条件**：
- 技术栈升级评估
- 架构重构的前期调研
- 性能瓶颈的技术方案
- 安全问题的解决方案

## 必需的文件夹结构

```
.claude/
├── subagents/
│   ├── config/           # subagents配置文件
│   ├── prompts/          # 专业提示词库
│   ├── contexts/         # 上下文缓存
│   ├── templates/        # 文档模板
│   └── logs/            # 执行日志
├── contexts/
│   ├── project/         # 项目级上下文
│   │   ├── overview.md      # 项目概览
│   │   ├── tech-stack.md    # 技术栈说明
│   │   ├── architecture.md  # 架构文档
│   │   └── standards.md     # 编码规范
│   ├── code/            # 代码分析结果
│   │   ├── analysis/        # 分析报告
│   │   ├── snippets/        # 代码片段
│   │   └── dependencies/    # 依赖图谱
│   └── knowledge/       # 知识库
│       ├── best-practices/  # 最佳实践
│       ├── patterns/        # 设计模式
│       └── security/        # 安全规范
├── shared/
│   ├── templates/       # 共享模板
│   ├── scripts/         # 通用脚本
│   └── configs/         # 配置文件模板
└── workspace/
    ├── temp/            # 临时工作区
    ├── cache/           # 缓存文件
    └── output/          # 输出结果
```

## MCP服务配置需求

### 必需的MCP服务

1. **文件系统服务 (mcp-filesystem)**
   ```json
   {
     "name": "filesystem",
     "command": "uvx mcp-server-filesystem",
     "args": ["--base-dir", "/workspace"]
   }
   ```

2. **Git服务 (mcp-git)**
   ```json
   {
     "name": "git",
     "command": "uvx mcp-server-git",
     "args": ["--repository", "."]
   }
   ```

3. **进程管理服务 (mcp-process)**
   ```json
   {
     "name": "process",
     "command": "uvx mcp-server-process"
   }
   ```

4. **网络服务 (mcp-fetch)**
   ```json
   {
     "name": "fetch",
     "command": "uvx mcp-server-fetch"
   }
   ```

### 可选的增强MCP

5. **数据库服务 (mcp-sqlite)**
   ```json
   {
     "name": "database",
     "command": "uvx mcp-server-sqlite",
     "args": ["--db-path", ".claude/knowledge.db"]
   }
   ```

6. **搜索服务 (mcp-ripgrep)**
   ```json
   {
     "name": "search",
     "command": "uvx mcp-server-ripgrep"
   }
   ```

## 配置文件模板

### subagents配置文件 (.claude/subagents/config.json)
```json
{
  "subagents": {
    "code-analyzer": {
      "enabled": true,
      "triggers": ["code-change", "performance-issue", "security-audit"],
      "priority": "high",
      "timeout": 30000,
      "context": ["codebase", "dependencies", "performance-metrics"]
    },
    "doc-writer": {
      "enabled": true,
      "triggers": ["api-creation", "function-complexity", "release-prep"],
      "priority": "medium",
      "timeout": 15000,
      "context": ["api-specs", "code-comments", "project-structure"]
    },
    "test-planner": {
      "enabled": true,
      "triggers": ["feature-complete", "bug-fix", "coverage-low"],
      "priority": "high",
      "timeout": 20000,
      "context": ["test-coverage", "code-changes", "requirements"]
    },
    "config-manager": {
      "enabled": true,
      "triggers": ["project-init", "env-migration", "dependency-update"],
      "priority": "medium",
      "timeout": 25000,
      "context": ["environment", "dependencies", "deployment-config"]
    },
    "tech-researcher": {
      "enabled": true,
      "triggers": ["tech-upgrade", "architecture-review", "performance-research"],
      "priority": "low",
      "timeout": 60000,
      "context": ["tech-stack", "requirements", "constraints"]
    }
  }
}
```

### 项目上下文模板 (.claude/contexts/project/overview.md)
```markdown
# 项目概览

## 基本信息
- 项目名称：
- 项目类型：[Web应用/API服务/库/工具]
- 主要语言：
- 框架/库：

## 技术栈
- 前端：
- 后端：
- 数据库：
- 部署：

## 项目结构
- 核心模块：
- 关键路径：
- 配置文件：

## 开发规范
- 代码风格：
- 提交规范：
- 测试要求：

## 部署信息
- 环境配置：
- CI/CD流程：
- 监控方案：
```

## 实施步骤

### 第一阶段：基础设施搭建
1. 创建文件夹结构
2. 安装和配置MCP服务
3. 建立基础配置文件
4. 创建上下文模板

### 第二阶段：核心subagents实现
1. 实现code-analyzer的基础功能
2. 实现doc-writer的模板系统
3. 建立subagents间的通信机制
4. 测试协作流程

### 第三阶段：高级功能开发
1. 实现test-planner的测试策略
2. 实现config-manager的自动化配置
3. 实现tech-researcher的调研功能
4. 优化性能和用户体验

### 第四阶段：监控与优化
1. 建立性能监控
2. 收集用户反馈
3. 持续改进算法
4. 扩展新功能

## 关键成功指标

- **效率提升**：任务完成时间减少50%以上
- **质量改善**：代码审查发现的问题减少30%
- **文档覆盖率**：API文档覆盖率提升到90%以上
- **测试覆盖**：代码覆盖率提升到80%以上
- **用户满意度**：用户反馈评分4.5/5以上

## 扩展性考虑

- **插件架构**：支持第三方subagents开发
- **多语言支持**：适配不同编程语言项目
- **团队协作**：支持多人协作模式
- **云端同步**：支持上下文和配置的云端同步