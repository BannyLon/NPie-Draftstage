---
type: "inbox"
status: "pending"
标题：: "Karpathy's LLM Wiki as Agent Memory"
链接：: "https://aaif.io/blog/karpathys-llm-wiki-as-agent-memory/"
来源：: "Agentic AI Foundation (AAIF)"
剪藏时间：: "2026-06-25 17:49"
网页摘要：: "At work, I’m building agents to handle various operational tasks and have found Karpathy’s LLM Wiki design to be an excellent solution for implementing most types of memory for my agents.The LLM wiki is a simple yet powerful collection of interlinked markdown files that are updated as the LLM gains more knowledge."
---
## 🤖 AI 智能解析
> [!brain] 核心摘要
> 本文介绍了作者利用Karpathy提出的LLM Wiki设计来构建代理记忆系统的实践，该系统由原始资料、Wiki和模式三层组成，原始资料作为不可变的真实来源，Wiki是由大语言模型维护的结构化知识库，包含索引、日志和各类知识页面，模式则通过AGENTS.md文件指导代理如何维护Wiki，这种设计巧妙地映射了语义、实体、情景、摘要和程序五种记忆类型，作者以会议管理代理为例展示了其如何通过Wiki实现跨会话的知识存储、精炼和检索，虽然未覆盖会话和工作记忆等短时记忆类型，但作为持久记忆方案非常实用。

> [!list] 关键要点 (Key Facts)
> > - LLM Wiki架构由三个层次组成：不可变的原始资料层、大语言模型维护的结构化知识库Wiki层和指导维护的AGENTS.md模式层。
> - 该模式能有效映射五种代理记忆类型：实体记忆（如演讲者页面）、语义记忆（如趋势页面）、情景记忆（如日志文件）、摘要记忆（如压缩后的来源摘要）和程序记忆（AGENTS.md中的维护规则）。
> - Wiki作为持久外部记忆层，让代理无需在每次会话中重读所有原始资料，通过索引导航和可选的搜索工具即可高效检索知识。

---

## 📌 我的网页划线
> [!tip] 提示
> 如果你在网页上用鼠标选中文本并高亮，它们会出现在这里。如果不划线，此处会自动隐藏或留空。


---

## 📄 剪藏正文

---

Lately, I’ve been down a rabbit hole exploring [agent memory](https://angiejones.tech/agent-memory/).

What makes it so fascinating is all of the various types of memory we need to consider when building agents.

| **Conversational** | Stores the messages exchanged between the user and assistant so the agent can refer back to prior turns in the conversation. |
| --- | --- |
| **Semantic** | Stores durable facts and meanings that should outlive the exact conversation where they were learned. |
| **Episodic** | Stores events: what happened, when it happened, what actions were taken, and what outcomes occurred. |
| **Procedural** | Stores knowledge about how to do things, including workflows, rules, steps, and reusable processes. |
| **Entity** | Stores facts about specific people, accounts, projects, systems, objects, or other named entities. |
| **Working** | Stores temporary information used while reasoning through the current task; usually short lived and not meant to persist forever. |
| **Summary** | Stores compressed versions of longer conversations, documents, threads, or contexts so the agent can retain the important points without replaying everything. |

At work, I’m building agents to handle various operational tasks and have found [Karpathy’s LLM Wiki design](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) to be an excellent solution for implementing most types of memory for my agents.

The LLM wiki is a simple yet powerful collection of interlinked markdown files that are updated as the LLM gains more knowledge.

## LLM Wiki Architecture

The wiki itself is one of three layers that make up the system.

`raw sources → wiki → schema`

You provide the original sources, the LLM maintains a wiki derived from those sources, and a schema file tells the LLM how to consistently maintain the wiki.

### Raw Sources

The first layer is the raw sources, which is the input the agent consumes (e.g. documents, articles, notes, etc). Raw sources are considered the immutable source of truth. The agent can read them, summarize them, and use them as evidence, but it should not modify them.

### Wiki

The second layer is the wiki itself which is the structured markdown knowledge base the LLM maintains. This is where the agent starts connecting the dots across everything it has seen and gradually creates a knowledge base it can keep coming back to.

In addition to the knowledge pages, the wiki also includes two special files: `index.md` which helps the agent (and human) navigate the knowledge base, and `log.md` which preserves a chronological record of ingests, queries, lint passes, and other activity.

### Schema

The schema is the instruction layer that tells the agent how to maintain the wiki. This is usually an `AGENTS.md` file explaining conventions, workflows, and structure the agent should follow to keep the wiki intact.

## How the Wiki Becomes Memory

While Karpathy’s LLM wiki is not branded as a formal agent memory architecture, it maps surprisingly well to how agent memory works in practice.

It treats a maintained wiki, supported by raw sources and an instructional schema, as an external memory layer by giving the agent somewhere persistent to store, refine, and retrieve knowledge across sessions.

The raw sources are the evidence layer. They are not really memory in the agentic sense but they are the original records of information. They can contain facts, events, conversations, procedures, and entity details, but they are unprocessed. Think of them as the things memories are built from.

Together, the wiki and its schema support several memory functions:

- **Semantic memory:** stores durable facts and synthesized knowledge
- **Entity memory:** contains pages about people, projects, systems, etc
- **Episodic memory:** captures logs and records of what happened
- **Summary memory:** stores compressed versions of longer material
- **Procedural memory:** encodes how the agent should maintain the wiki

The schema defines the agent’s memory maintenance or “dreaming” routines, with linting the wiki being one example.

## Example of LLM Wiki as Memory

Here’s an example of what this looks like in practice.

I am the program chair for several global conferences this year, which means I have to stay on top of trends, speakers, and sessions – thousands of them. I built an agent that reads raw event materials then maintains a wiki with all of this data.

```js
event-memory/
├── AGENTS.md                    # Schema: how the agent maintains the wiki
├── raw/                         # Immutable source materials 
│   ├── events/                 # Raw event-specific materials
│   └── sources/                # Raw external/public sources
└── wiki/                        # LLM-maintained knowledge base
    ├── index.md                 # Content catalog of wiki pages and summaries
    ├── log.md                   # Chronological record of ingest and updates
    ├── events/                  # Summaries: dates, tracks, themes
    ├── sessions/                # Session pages: title, abstract summary
    │   ├── building-reliable-agents.md
    │   └── evaluating-agent-workflows.md
    ├── speakers/                # Speaker pages: bio, affiliation, sessions
    │   ├── speaker-a.md
    │   └── speaker-b.md
    ├── sources/                 # Summaries from articles, reports, discussions
    ├── trends/                  # Evolving patterns over time
    └── topics/                  # Topic summaries
```

Together, the raw sources, schema, and wiki form the agent’s long term memory layer. This helps the agent understand how trends are evolving, what topics should be covered at a given conference, and which sessions address current trends.

### Entity Memory

The wiki provides entity memory through its pages for speakers, sessions, events, topics, and other named things the agent needs to reason about.

```js
wiki/speakers/angie-jones.md
wiki/sessions/building-mcp-servers.md
wiki/events/mcp-dev-summit-2026-mumbai.md
wiki/topics/authorization.md
```

Each page gives the agent a place to keep track of what it knows about that entity and how it relates to everything else in the system.

For example, the agent may know:

- which speakers are presenting at an event
- which sessions belong to a topic area
- which topics are appearing across multiple events
- what company or project a speaker represents
- which sessions a speaker has delivered
- how speakers, sessions, topics, and events connect to broader trends

Over time, those relationships become just as valuable as the individual facts themselves. Instead of seeing a collection of disconnected pages, the agent can understand how people, events, sessions, and ideas fit together.

That is a clear demonstration of entity memory.

### Semantic Memory

Trend pages are perhaps the clearest example of semantic memory because they capture patterns and meanings extracted from many sources over time.

The agent looks across what’s happening in the ecosystem then stores the meanings across many events.

The trend pages tell the agent things like:

- MCP builders are increasingly concerned with controlling what tools can do, who/what can invoke them, how actions are approved, and how execution is audited across trust boundaries.
- Tool-loading and context-budget pressure remain active practical pain points.
- Agentic AI trust increasingly depends on operational controls and observability, not just orchestration or autonomy.

Semantic memory also appears throughout the rest of the wiki. Topic pages, speaker pages, session pages, and source summaries all preserve information that can be reused across future events and future agent sessions.

### Episodic Memory

Episodic memory is the “what happened, when, and what changed” layer of the system. In my example, it shows up mainly in log.md, dated source refresh pages, and trend history records.

This allows me to interrogate the agent with questions such as when a topic first appeared or when a trend started phasing out.

### Summary Memory

Summary memory appears throughout the wiki as the agent continuously compresses larger sources into more useful knowledge artifacts.

For example, to gather trends, the agent reads live raw material from all over the web. It then compresses it into consumable summaries. Instead of preserving every post and comment from a discussion thread, it writes a summarized source page like:

`wiki/sources/mcp/mcp-remote-runtime-auth-registry-sprawl-refresh-2026-06-01.md`

That page is a compressed representation of a larger evidence set. It’s effectively turning all that noise into knowledge the agent can build on.

The same pattern shows up across the wiki in several places. Session abstracts become summarized session pages, speaker biographies become short speaker pages, and collections of related sessions become topic summaries.

Summary memory is key for performance because in future sessions, agents don’t need to re-read every raw source every time. They can start from the summarized source page, then inspect raw links only when needed.

As the wiki grows, retrieval becomes increasingly important. Small wikis can often be navigated through the index alone, but larger ones may benefit from search tools, embeddings, vector search, reranking, or other retrieval mechanisms. In this model, however, those technologies support the memory system rather than define it. The memory is the maintained body of knowledge itself. Search simply helps the agent navigate it.

### Procedural Memory

Like any memory system, the wiki requires maintenance. The schema layer (`AGENTS.md`) functions much like procedural memory by encoding how knowledge is merged, updated, corrected, and occasionally retired as new evidence arrives.

It has rules for:

- avoiding duplicate pages
- decaying stale trends
- distinguishing one-off event observations from reusable cross-event knowledge
- updating existing canonical pages instead of creating clutter
- logging meaningful operations
- keeping the index current

All of this is handled by the agent itself, not the human. This beautifully implements Karpathy’s “LLM as wiki bookkeeper” idea.

## The Memory Was There All Along

A wiki is such a simple concept, while memory is quite a complex one. Yet at the end of the day, both are really forms of knowledge management.

The real power of the LLM Wiki pattern is that it turns scattered information into a living memory system, even if it isn’t marketed as one.

The structure itself reveals the memory model:

```js
AGENTS.md          # procedural memory
wiki/
├── events/        # episodic + summary memory
├── sessions/      # entity + summary memory
├── speakers/      # entity memory
├── sources/       # summary + episodic memory
├── trends/        # semantic + episodic memory
├── topics/        # semantic memory
└── log.md         # episodic memory
```

That said, this pattern has not replaced every kind of memory for me. I’ve used LLM wikis with several agents, and I have not seen them implement conversational or working memory within the wiki. Those are usually short-lived memory types that my agents only need in-session, so the agent has not needed to preserve them as long-term memory.

For persistent memory, though, the wiki pattern has been the most practical approach I’ve used.