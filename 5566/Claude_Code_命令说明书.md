# Claude Code 命令说明书

## 概述
Claude Code v1.0.88 是一个强大的AI编程助手，能够帮助您进行代码开发、文件编辑、错误修复等任务。

**重要提醒：** 请始终审查Claude的响应，特别是在运行代码时。Claude具有当前目录的文件读取权限，可以在您的许可下运行命令和编辑文件。

## 使用模式

### 交互式模式
```bash
claude
```
启动交互式会话，可以与Claude进行实时对话。

### 非交互式模式
```bash
claude -p "问题"
```
直接向Claude提问，无需进入交互式会话。

### 查看所有命令行选项
```bash
claude -h
```

## 常用任务

### 代码相关问题
- **询问代码库相关问题** > `How does foo.py work?` (foo.py是如何工作的？)
- **编辑文件** > `Update bar.ts to...` (更新bar.ts文件...)
- **修复错误** > `cargo build` (构建项目)

### 运行命令
- **获取帮助** > `/help`
- **运行bash命令** > `!ls`

## 交互模式命令列表

### 目录和工作区管理
- **`/add-dir`** - 添加新的工作目录
- **`/bashes`** - 列出和管理后台bash shell

### 代理和配置管理
- **`/agents`** - 管理代理配置
- **`/config`** - 打开配置面板
- **`/model`** - 设置Claude Code的AI模型
- **`/permissions`** - 管理工具权限规则（允许和拒绝）

### 会话和上下文管理
- **`/clear`** - 清除对话历史并释放上下文
- **`/compact`** - 清除对话历史但保留上下文摘要。可选：`/compact [摘要说明]`
- **`/context`** - 以彩色网格形式可视化当前上下文使用情况
- **`/resume`** - 恢复对话

### 状态和监控
- **`/cost`** - 显示当前会话的总成本和持续时间
- **`/status`** - 显示Claude Code状态，包括版本、模型、账户、API连接性和工具状态
- **`/statusline`** - 设置Claude Code的状态行UI

### 诊断和维护
- **`/doctor`** - 诊断和验证您的Claude Code安装和设置
- **`/migrate-installer`** - 从全局npm安装迁移到本地安装
- **`/upgrade`** - 升级到Max以获得更高的速率限制和更多Opus功能

### 集成和扩展
- **`/ide`** - 管理IDE集成并显示状态
- **`/init`** - 使用代码库文档初始化新的CLAUDE.md文件
- **`/install-github-app`** - 为仓库设置Claude GitHub Actions
- **`/mcp`** - 管理MCP服务器
- **`/hooks`** - 管理工具事件的钩子配置

### 账户管理
- **`/login`** - 使用您的Anthropic账户登录
- **`/logout`** - 从您的Anthropic账户登出

### 输出和导出
- **`/output-style`** - 直接设置输出样式或从选择菜单设置
- **`/output-style:new`** - 创建自定义输出样式
- **`/export`** - 将当前对话导出到文件或剪贴板

### GitHub集成
- **`/pr-comments`** - 从GitHub拉取请求获取评论
- **`/review`** - 审查拉取请求
- **`/security-review`** - 完成当前分支上待处理更改的安全审查

### 编辑模式
- **`/vim`** - 在Vim和普通编辑模式之间切换

### 终端设置
- **`/terminal-setup`** - 安装Shift+Enter键绑定用于换行

### 反馈和帮助
- **`/bug`** - 提交关于Claude Code的反馈
- **`/help`** - 显示帮助和可用命令
- **`/release-notes`** - 查看发布说明
- **`/memory`** - 编辑Claude记忆文件

### 退出
- **`/exit`** - 退出REPL

## 学习资源
更多信息请访问：https://docs.anthropic.com/s/claude-code

---

*本说明书基于Claude Code v1.0.88版本编写，如有更新请参考官方文档。*
