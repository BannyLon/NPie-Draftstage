---
title: My-Viki_System
type: synthesis
tags: [my-viki, system, overview, llm-wiki, implementation]
sources: ["raw/Karpathy's LLM Wiki as Agent Memory.md", "raw/What Is Andrej Karpathy's LLM Wiki? How to Build a Personal Knowledge Base With Claude Code.md"]
last_updated: 2026-06-25
---

# My-Viki System

## 什么是 My-Viki

**My-Viki** 是本知识库的系统名称，它是 [[LLM_Wiki]] 模式的一个具体实现实例。名字来源于 "My Wiki" 的变体拼写，意在强调这是一个**个人化的、活的（Vivid）知识系统**。

My-Viki 严格遵循 Karpathy 的 LLM Wiki 设计理念，并根据本地的实际需求进行了定制化配置。

## 设计哲学

### 核心信念

1. **知识应该复利**：每次学习不应是孤立事件，而应为未来积累。详见 [[Compounding_Knowledge]]
2. **人类策展，机器维护**：人的价值在于判断和创造，LLM 的价值在于整理和连接。详见 [[Second_Brain]]
3. **结构先于内容**：一个好的框架比 100 篇散乱的笔记更有价值
4. **简单胜过复杂**：整个系统基于文件系统 + Markdown + Git，不依赖任何专有格式

### 与其他方案的区别

| 方案 | 维护者 | 链接方式 | 知识复利 |
|---|---|---|---|
| 传统笔记（Notion/Obsidian 手动） | 人类 | 手动建立 | 缓慢且容易停滞 |
| RAG 系统（NotebookLM） | 无持续维护 | 无持久链接 | 无 — 每次查询独立 |
| **My-Viki（LLM Wiki）** | **LLM 自动** | **自动双向链接** | **持续复利** |

## 系统架构

### 文件结构

```
My-WIKI/
├── CLAUDE.md              ← 行为规则（LLM 的角色和工作流定义）
├── llm-wiki.md            ← Karpathy 原始设计文档（参考，只读）
├── raw/                   ← 原始资料的收件箱（人类添加，LLM 只读）
│   ├── Karpathy's LLM Wiki as Agent Memory.md
│   ├── LLM Knowledge Bases.md
│   └── What Is Andrej Karpathy's LLM Wiki? How to Build...
├── wiki/                  ← 编译知识库（LLM 维护）
│   ├── index.md           ← 知识总目录
│   ├── log.md             ← 操作日志
│   ├── WIKI.md            ← 结构 Schema 说明
│   ├── concepts/          ← 概念类页面
│   ├── entities/          ← 实体类页面
│   ├── sources/           ← 源文档摘要
│   ├── synthesis/         ← 综合分析
│   ├── comparisons/       ← 对比分析
│   └── meta/              ← 元信息
└── .obsidian/             ← Obsidian 工作区配置
```

### 工具链

- **编辑器/浏览器**：Obsidian（查看 wiki、图谱视图、反向链接面板）
- **LLM 引擎**：Claude Code（执行 ingest / query / lint 工作流）
- **版本控制**：Git（追踪所有 wiki 变更历史）
- **内容捕获**：Obsidian Web Clipper（将网页转为 Markdown 放入 `raw/`）

## 当前状态

- **初始化日期**：2026-06-25
- **raw/ 文档数**：3 份待 ingest
- **wiki/ 页面数**：11 个（8 个核心概念 + index + log + WIKI.md）
- **下一步**：执行首次 ingest，处理 `raw/` 中的 3 份源文档

## 演进路线

### 短期（初始化阶段）
- [x] 建立目录结构和 schema（CLAUDE.md + WIKI.md）
- [x] 生成核心概念页面作为知识骨架
- [ ] 对 raw/ 中的 3 份文档执行首次 ingest
- [ ] 创建对应的 source-summary 页面和实体页面

### 中期（常规运营）
- [ ] 建立稳定的 ingest 节奏
- [ ] 开始在日常 Query 中回写有价值的 synthesis 页面
- [ ] 首次 lint 检查

### 长期（持续演进）
- [ ] 根据实际使用反馈优化 schema 和 CLAUDE.md
- [ ] 探索 Marp 幻灯片生成
- [ ] 评估是否需要引入搜索工具（如 qmd）
- [ ] 考虑建立跨项目的知识网络

## 相关页面

- [[WIKI]] — 详细的 Schema 说明
- [[LLM_Wiki]] — 底层模式定义
- [[Ingest_Query_Lint_Workflow]] — 日常操作指南
- [[Raw_Wiki_Layered_Architecture]] — 架构设计原理
