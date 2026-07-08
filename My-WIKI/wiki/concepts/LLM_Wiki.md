---
title: LLM_Wiki
type: concept
tags: [llm-wiki, pkm, architecture, knowledge-management]
sources: ["raw/Karpathy's LLM Wiki as Agent Memory.md", "raw/What Is Andrej Karpathy's LLM Wiki? How to Build a Personal Knowledge Base With Claude Code.md"]
last_updated: 2026-06-25
---

# LLM Wiki

## 定义

**LLM Wiki** 是由 [[Andrej_Karpathy]] 提出的一种个人知识库构建模式。其核心思想是：**让 LLM 作为 wiki 的主要撰写者和维护者，持续将原始资料编译为结构化、互相链接的 Markdown 页面**，而非每次查询时从原始文档中临时检索（RAG 模式）。

## 核心原理

### 与传统 RAG 的本质区别

| 维度 | 传统 RAG | LLM Wiki |
|---|---|---|
| 知识存储 | 原始文档 + 向量索引 | 结构化 wiki 页面 |
| 查询方式 | 每次从 chunk 检索后即时生成答案 | 基于已编译的 wiki 页面回答问题 |
| 知识积累 | 无 — 每次查询独立 | 持续积累 — 知识复利 |
| 交叉引用 | 不存在 | 双向链接密集 |
| 矛盾标记 | 无法标记 | 显式标注 |

### 三层架构

LLM Wiki 的核心架构借鉴了 Karpathy 的设计，由三个层次组成：

1. **Raw 层（原始资料）**：只读的源文档集合，如文章、笔记、论文等。LLM 可读取但绝不修改。详见 [[Raw_Wiki_Layered_Architecture]]。
2. **Wiki 层（编译知识）**：LLM 生成和维护的结构化 Markdown 页面集合，包含概念页、实体页、源摘要、综合分析等。
3. **Schema 层（规则配置）**：通过 `CLAUDE.md` 和 `WIKI.md` 等文件定义 wiki 的结构规范、页面类型和工作流行为。

### 三大操作

LLM Wiki 的日常运作围绕三个核心操作展开，详见 [[Ingest_Query_Lint_Workflow]]：

- **Ingest（摄取）**：将 `raw/` 中的新资料编译为 wiki 页面
- **Query（查询）**：基于 wiki 知识回答问题，并可将有价值的答案回写为 wiki 页面
- **Lint（维护）**：定期检查 wiki 健康状态，发现矛盾、孤立页面、坏链接

## 为什么这个模式有效

维护知识库的繁琐之处不在于阅读或思考，而在于**记账式劳动**——更新交叉引用、保持摘要时效、标记新旧信息的矛盾、维护数十个页面的一致性。人类放弃 wiki 是因为维护负担的增长速度超过价值增长速度。而 LLM 不会厌倦、不会忘记更新交叉引用，可以在一次操作中触及 15 个文件。维护成本趋近于零。

人类的职责是：策展来源、引导分析方向、提出好问题、思考这些信息意味着什么。LLM 的职责是其余一切。

这一思想在精神上与 Vannevar Bush 1945 年提出的 **Memex** 系统（一种带有联想轨迹的个人策展知识库）相通。Bush 未能解决的核心问题是"谁来做维护"——LLM 解决了这个问题。

## 关键特征

- **持久化的复合产物**：wiki 不是一次性产物，而是随时间不断丰富的知识资产
- **LLM 驱动维护**：人类策展，LLM 执行所有"脏活累活"
- **工具无关**：可与 Obsidian、VS Code 等任何 Markdown 编辑器配合使用
- **Git 原生**：wiki 即 Git 仓库，天然获得版本控制、分支和协作能力
- **知识复利效应**：随着页面和链接增长，wiki 的价值呈超线性增长。详见 [[Compounding_Knowledge]]

## 与其他概念的关系

- [[Compounding_Knowledge]] — 解释为什么 wiki 结构能产生知识复利
- [[Personal_Knowledge_Management]] — LLM Wiki 是 PKM 的一种具体实践范式
- [[Second_Brain]] — LLM Wiki 可视为一种"第二大脑"的实现方案
- [[Raw_Wiki_Layered_Architecture]] — 详细说明三层架构的设计决策
- [[Knowledge_Graph_and_Bidirectional_Links]] — 双向链接是 wiki 复利的关键机制

## 实践建议

1. 从少量源文档开始，先建立 wiki 骨架，再逐步 ingest
2. 每次 ingest 后浏览 Obsidian 的图谱视图，直观感受知识结构的变化
3. 定期执行 lint 操作，防止 wiki 腐化
4. 将好的 Query 回答回写为 wiki 页面，让探索也产生复利
