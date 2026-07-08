---
title: Raw_Wiki_Layered_Architecture
type: concept
tags: [architecture, llm-wiki, design, raw, wiki]
sources: ["raw/Karpathy's LLM Wiki as Agent Memory.md"]
last_updated: 2026-06-25
---

# Raw / Wiki 分层架构

## 定义

**Raw / Wiki 分层架构** 是 [[LLM_Wiki]] 模式的物理基础设计。它通过在文件系统层面将"原始资料"与"编译知识"严格分离，实现了知识处理管道的清晰边界和可审计性。

## 架构总览

```
My-Viki Vault/
├── CLAUDE.md          ← Schema 层：行为规则与工作流定义
├── llm-wiki.md        ← 参考层：Karpathy 原始设计文档（只读）
├── raw/               ← Raw 层：原始资料（LLM 只读）
│   ├── article_1.md
│   ├── article_2.md
│   └── ...
├── wiki/              ← Wiki 层：编译知识（LLM 读写）
│   ├── index.md       ← 知识总目录
│   ├── log.md         ← 操作日志
│   ├── WIKI.md        ← 结构说明文档
│   ├── concepts/      ← 概念类页面
│   ├── entities/      ← 实体类页面
│   ├── sources/       ← 源文档摘要
│   ├── synthesis/     ← 综合分析
│   ├── comparisons/   ← 对比页面
│   └── meta/          ← 元信息
└── .obsidian/         ← Obsidian 配置（工具层）
```

## 三层设计详解

### Raw 层：不可变的原始资料

**核心约束**：LLM **绝不修改或删除** `raw/` 中的任何文件内容。

**设计理由**：
- **保留溯源能力**：wiki 中的任何结论都可以追溯到原始出处
- **防止信息污染**：原始资料作为 ground truth，不受 LLM 加工过程的影响
- **支持重新编译**：当 schema 或理解框架演进时，可以用新的视角重新 ingest 旧的 raw 资料

**典型内容**：
- 网页文章的 Markdown 版本（通过 Obsidian Web Clipper 等工具捕获）
- PDF 转录文本
- 会议记录、访谈笔记
- 项目文档原稿

### Wiki 层：LLM 维护的结构化知识

**核心原则**：只有 `wiki/` 目录内的内容可以被 LLM 创建和修改。

**设计理由**：
- **清晰的修改边界**：LLM 知道在哪里可以写、在哪里绝对不能写
- **Git 友好的变更追踪**：`raw/` 只由人类添加，`wiki/` 由 LLM 维护——两者的 git diff 语义完全不同
- **可重建性**：理论上，删除整个 `wiki/` 并用相同的 `raw/` 和 `CLAUDE.md` 重新运行 ingest，应该能重建出等价的知识库（虽然具体页面可能不完全相同）

**子目录组织**：

| 子目录 | 页面类型 | 说明 |
|---|---|---|
| `concepts/` | concept | 抽象概念、方法论、框架 |
| `entities/` | entity | 人物、组织、工具、产品 |
| `sources/` | source-summary | 对应 raw 文件的摘要 |
| `synthesis/` | synthesis | 跨来源的综合分析 |
| `comparisons/` | comparison | 对比分析 |
| `meta/` | meta | 元信息和工具页面 |

### Schema 层：行为规则

**核心文件**：
- `CLAUDE.md`：定义 LLM 的角色、行为准则和三大工作流
- `wiki/WIKI.md`：定义 wiki 的结构规范、页面类型和 YAML 字段约定
- `llm-wiki.md`：Karpathy 的原始设计文档（参考，不直接作为操作规范）

Schema 层的优先级：`CLAUDE.md` > `wiki/WIKI.md` > `llm-wiki.md`

## 分层架构的价值

1. **关注点分离**：人类负责策展（往 `raw/` 加东西），LLM 负责编译（在 `wiki/` 产生价值），各司其职
2. **防错设计**：即使 LLM 产生幻觉或错误，`raw/` 中的原始资料始终完好
3. **渐进演进**：可以先建立分层结构，再逐步完善 schema——分层本身是最小可行架构
4. **工具无关**：分层设计不依赖特定工具，只依赖文件系统和 Markdown

## 与其他概念的关系

- [[LLM_Wiki]] — 分层架构是 LLM Wiki 的物理实现
- [[Ingest_Query_Lint_Workflow]] — ingest 工作流的核心操作就是从 raw 到 wiki 的编译
- [[Compounding_Knowledge]] — 分层架构为知识复利提供了物理基础

## 实践要点

1. **raw/ 就是你的收件箱**：任何可能有价值的内容都扔进去
2. **wiki/ 是你的图书馆**：只放 LLM 整理过的结构化知识
3. **不要把 raw/ 当 wiki 用**：不要在 raw/ 里手动整理笔记——那是 LLM 的工作
4. **保护好 raw/ 的纯度**：不要在里面做编辑、标注或评论
