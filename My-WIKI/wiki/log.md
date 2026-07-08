---
title: My-Viki 操作日志
type: synthesis
tags: [log, meta, chronology]
last_updated: 2026-06-25
---

# My-Viki 操作日志

按时间倒序记录所有 ingest、大改动、维护操作。只追加，不改历史。

---

## [2026-06-25] init | My-Viki 系统初始化

**操作类型**: 系统初始化

**变更摘要**:
- 创建 `wiki/` 子目录结构：`concepts/`, `entities/`, `sources/`, `synthesis/`, `comparisons/`, `meta/`
- 生成 `wiki/index.md`（知识总目录）
- 生成 `wiki/log.md`（本文件）
- 创建 8 个核心概念页面：
  - `wiki/concepts/LLM_Wiki.md`
  - `wiki/concepts/Compounding_Knowledge.md`
  - `wiki/concepts/Personal_Knowledge_Management.md`
  - `wiki/concepts/Second_Brain.md`
  - `wiki/concepts/Ingest_Query_Lint_Workflow.md`
  - `wiki/concepts/Raw_Wiki_Layered_Architecture.md`
  - `wiki/concepts/Knowledge_Graph_and_Bidirectional_Links.md`
  - `wiki/synthesis/My-Viki_System.md`

**初始状态**: 知识库骨架搭建完成，`raw/` 中有 3 份待 ingest 的源文档。

**下一步**: 对 `raw/` 中的源文档执行首次 ingest。
