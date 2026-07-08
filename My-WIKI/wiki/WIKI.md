# WIKI.md｜My‑Viki 结构与 Schema 说明

本文件是 My‑Viki 的「结构说明书 / schema 文档」，专门描述：

- `wiki/` 目录的组织方式；
- 支持的页面类型及含义；
- YAML 前言（frontmatter）的字段规范；
- 文件命名与链接约定；
- 和 Karpathy LLM Wiki 思路对齐的基本组织规则。

它为两类读者服务：

1. 人类的你：日后回来看得懂自己当初是怎么设计的。
2. Claude / 其他 LLM：在需要了解结构细节时，可以读取本文件作为参考。

核心原则：**raw/ 放原始资料（只读），wiki/ 放编译后的结构化知识（可写）。**

---

## 1. 顶层目录结构（详细版）

My‑Viki Vault 顶层主要目录约定如下：

- `CLAUDE.md`  
  行为规则文件，描述 My‑Viki 的整体目标、角色定义、ingest/query/lint 工作流等。Claude 在每次会话启动时会优先阅读。

- `raw/`  
  原始资料目录（只读）。  
  用来放各种未加工的输入材料，例如：
  - 文章整理后的 Markdown；
  - 访谈记录；
  - 把 PDF / 网页转成 md 后的文本；
  - 项目文档原稿等。

  **LLM 不得修改 `raw/` 中任何文件的内容，只能读取。**

- `wiki/`  
  编译后的知识库目录（LLM 只在这里读写）：
  - `wiki/index.md`  
    知识总目录与导航。列出主要主题、子目录和重要页面链接。
  - `wiki/log.md`  
    操作日志，按时间顺序记录每次 ingest / 大改动。只追加，不改历史。
  - 其他子目录和页面（推荐结构）：
    - `wiki/concepts/`：概念类页面（concept）
    - `wiki/entities/`：实体类页面（entity）
    - `wiki/sources/`：源文档摘要（source-summary）
    - `wiki/synthesis/`：综合分析与整合性页面（synthesis）
    - `wiki/comparisons/`：对比类页面（comparison）
    - `wiki/meta/`：元信息与工具页面（例如本 WIKI.md、仪表盘等）

> 说明：具体子目录可以在实践中微调，但**一旦稳定下来，应更新本文件保持一致**。

---

## 2. 页面类型（type）定义

所有 `wiki/` 页面都应在 YAML 前言中包含一个 `type` 字段，并从以下枚举中选择：

- `concept`  
  抽象概念、方法论、框架、模型。  
  例如：`Compounding_Knowledge`, `Personal_Knowledge_Management`, `RAG_vs_Wiki`, `Obsidian_Workflow` 等。

- `entity`  
  具体实体，如人物、组织、产品、项目、工具等。  
  例如：某个作者、某个公司、某个课程、某个插件。

- `source-summary`  
  针对某个 `raw/xxx.md` 源文档的结构化摘要页面。  
  - 包含原文的关键信息、结构、主要论点、出处信息；
  - 应在 `sources` 字段中显式标注关联的 raw 文件路径。

- `synthesis`  
  跨多个来源与概念的综合性总结、结构化说明或主题长文。  
  例如：“关于 LLM Wiki 模式的整体实践指南”。

- `comparison`  
  针对多个对象进行对比的页面。  
  例如：“RAG_vs_Wiki” 对比传统 RAG 工作流与 LLM Wiki 工作流。

如需新增类型（如 `pattern`, `workflow` 等），请：

1. 在本文件中追加说明；
2. 为其设计最小结构示例；
3. 在后续页面中保持一致使用。

---

## 3. YAML 前言字段规范

每个 `wiki/` 页面顶部必须包含一段 YAML frontmatter，推荐的最小字段集为：

```yaml
---
title: 页面标题
type: concept | entity | source-summary | synthesis | comparison
tags: [tag1, tag2]
sources: ["raw/文件名1.md"]
last_updated: YYYY-MM-DD
---
```

### 字段含义

- `title`  
  - 页面主标题，一般与文中的第一个 `# 标题` 文本一致。  
  - 可以使用中文或英文，但建议与文件内容语义紧密相关。

- `type`  
  - 指定页面的角色，必须是上文列出的几种之一。  
  - 方便后续用脚本 / 查询对不同类型页面做过滤与统计。

- `tags`  
  - 自由标签。建议控制在少量、稳定的关键词，例如：`[llm-wiki, pkm, obsidian]`。  
  - 用于横向检索、后续可能的 Dataview / Bases 视图。

- `sources`  
  - 该页面**直接基于哪些 `raw/` 文件**整理而来。  
  - 用相对路径字符串数组表示，如：`["raw/karpathy_llm_wiki.md"]`。  
  - 若是纯自发总结（不对应某个具体 raw 文件），可以留空或省略。

- `last_updated`  
  - 最近一次实质内容更新的日期，格式 `YYYY-MM-DD`。  
  - 当 Claude 修改页面后，应尝试将此字段更新为当前日期。

可以按需扩展额外字段（例如 `status`, `importance`, `owner` 等），但**扩展时应同步更新本 WIKI.md 的说明**。

---

## 4. 文件命名与链接约定

### 4.1 文件命名

为兼顾可读性与跨平台兼容性，推荐如下命名方式：

- 文件名使用 **英文 + 下划线 `_`**，例如：
  - `Compounding_Knowledge.md`
  - `LLM_Wiki_Pattern.md`
  - `Personal_Knowledge_Management.md`
  - `RAG_vs_Wiki.md`
  - `Obsidian_Workflow.md`

- 对于时间敏感或日记型页面，可以在前面加时间戳或日期前缀，例如：
  - `2026-06-23_Weekly_Review.md`
  - `20260101_Annual_Planning.md`

命名不是强制必须英文，但强烈建议避免在文件名中使用过多特殊符号，以减少脚本与不同系统间的摩擦。

### 4.2 链接规范（Obsidian 风格）

- 内部链接统一使用 Obsidian 的 wikilink 语法：`[[页面标题]]`。  
- 链接中不写 `.md` 后缀。  
- 当某个主题在多个页面中出现并逐渐重要时，应：
  1. 为其创建独立页面（通常 type 为 `concept` 或 `entity`）；  
  2. 在相关页面中把原来的纯文本替换为 `[[该页面标题]]`；  
  3. 在该独立页面里增加“相关页面”小节，反向链接回主要上下文。

> 目标：**将主要知识点逐渐从“隐式提及”提升为“显式节点 + 双向链接”。**

---

## 5. 各类型页面的典型结构示例

以下示例仅为推荐模版。实际使用中，Claude 可以根据上下文对结构进行合理调整，但建议大体遵守。

### 5.1 concept 页面（概念）

```markdown
---
title: Compounding Knowledge
type: concept
tags: [knowledge, pkm, llm-wiki]
sources: ["raw/karpathy_llm_wiki.md"]
last_updated: 2026-06-23
---

# Compounding Knowledge

简要定义 + 来源说明。

## 核心要点

- 要点 1
- 要点 2
- 要点 3

## 与其他概念的关系

- 与 [[LLM_Wiki_Pattern]] 的关系
- 与 [[Personal_Knowledge_Management]] 的关系
- 与 [[RAG_vs_Wiki]] 的关系

## 实践建议

- 建议 1
- 建议 2
```

### 5.2 entity 页面（实体）

```markdown
---
title: Andrej Karpathy
type: entity
tags: [person, ai, llm-wiki]
sources: ["raw/karpathy_llm_wiki.md"]
last_updated: 2026-06-23
---

# Andrej Karpathy

简要介绍与背景。

## 关联概念与作品

- [[LLM_Wiki_Pattern]]
- [[Compounding_Knowledge]]
- [[Personal_Knowledge_Management]]

## 关联来源

- [[LLM_Wiki_Original_Source]]   <!-- 对应一个 source-summary 页面 -->
```

### 5.3 source-summary 页面（源文档摘要）

```markdown
---
title: LLM Wiki 原文概要
type: source-summary
tags: [source, llm-wiki]
sources: ["raw/karpathy_llm_wiki.md"]
last_updated: 2026-06-23
---

# LLM Wiki 原文概要

## 基本信息

- 原文作者：Andrej Karpathy
- 原始文件：`raw/karpathy_llm_wiki.md`

## 核心摘要

（用自己的话总结 3–5 段，覆盖主旨、结构与关键信息。）

## 提取出的主要概念与实体

- [[LLM_Wiki_Pattern]]
- [[Compounding_Knowledge]]
- [[Personal_Knowledge_Management]]
- [[RAG_vs_Wiki]]

## 备注与后续行动

- 还需要进一步 ingest 的相关材料
- 可能结合哪些已有页面做 synthesis
```

### 5.4 synthesis 页面（综合）

```markdown
---
title: LLM Wiki 模式在个人第二大脑中的落地
type: synthesis
tags: [llm-wiki, pkm, workflow]
sources: ["raw/karpathy_llm_wiki.md", "raw/your_notes_on_pkm.md"]
last_updated: 2026-06-23
---

# LLM Wiki 模式在个人第二大脑中的落地

## 问题背景

说明你试图解决的实际问题或场景。

## 核心思路

从 [[LLM_Wiki_Pattern]]、[[Compounding_Knowledge]]、[[Personal_Knowledge_Management]] 等页面抽取要点，综合说明。

## 实践步骤

- 步骤 1：搭建 My‑Viki 结构（raw/ + wiki/ + CLAUDE.md）
- 步骤 2：初始化基础概念页面
- 步骤 3：日常 ingest 与查询
- 步骤 4：定期 lint 与重构

## 开放问题与未来迭代

- 需要进一步验证的假设
- 后续可以尝试的改进方向
```

### 5.5 comparison 页面（对比）

```markdown
---
title: RAG_vs_Wiki
type: comparison
tags: [rag, llm-wiki, retrieval]
sources: ["raw/karpathy_llm_wiki.md"]
last_updated: 2026-06-23
---

# RAG vs Wiki

## 对比维度

- 存储形态
- 检索方式
- 上下文持久性
- 维护成本

## 传统 RAG 工作流

简要描述特点、优点、局限。

## LLM Wiki 工作流

简要描述特点、优点、局限，链接到 [[LLM_Wiki_Pattern]]。

## 总结与适用场景

- 何时偏向 RAG
- 何时更适合 LLM Wiki
- 如何在一个系统中混合使用两者
```

---

## 6. My‑Viki 工作流与 WIKI.md 的关系

- `CLAUDE.md`  
  描述 **行为准则和工作流**：  
  - Claude 在接到 “Ingest this: raw/xxx.md” 时要经历哪些步骤；  
  - 回答问题时如何优先使用 `wiki/`；  
  - Lint 检查时的流程与约束等。

- `WIKI.md`（本文件）  
  描述 **结构与 schema**：  
  - `wiki/` 下有哪些页面类型；  
  - 各类型的字段与结构长什么样；  
  - 命名与链接规范。

在你后续迭代 My‑Viki 时：

1. 如果你改变了目录结构、type 枚举、YAML 字段等，请优先更新本文件；
2. 如有必要，再同步更新 `CLAUDE.md` 中与工作流直接相关的描述；
3. 让 Claude 在需要理解结构细节时，先阅读本 WIKI.md，再结合 CLAUDE.md 的行为规则执行具体操作。

这样，My‑Viki 就既有“怎么干”的说明（CLAUDE.md），也有“干在什么结构上”的说明（WIKI.md），整体设计与 Karpathy 的 LLM Wiki 思路保持一致，并便于长期演进。