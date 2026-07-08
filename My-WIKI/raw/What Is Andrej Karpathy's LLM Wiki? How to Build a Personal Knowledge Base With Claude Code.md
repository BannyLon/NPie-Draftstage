---
type: "inbox"
status: "pending"
标题：: "What Is Andrej Karpathy's LLM Wiki How to Build a Personal Knowledge Base With Claude Code"
链接：: "https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code"
来源：: "MindStudio"
剪藏时间：: "2026-06-25 17:50"
网页摘要：: "Karpathy's LLM wiki turns raw documents into a structured markdown knowledge base Claude can query. Here's how to set it up in 5 minutes with Obsidian."
---
## 🤖 AI 智能解析
> [!brain] 核心摘要
> Karpathy提出的LLM维基理念主张用纯Markdown文件组织个人笔记和文档，使其成为LLM可直接推理的知识库，而非依赖传统笔记应用的手动浏览和搜索，用户通过Claude Code等AI工具以自然语言查询本地文件获取基于自身知识的精准答案。

> [!list] 关键要点 (Key Facts)
> 

---

## 📌 我的网页划线
> [!tip] 提示
> 如果你在网页上用鼠标选中文本并高亮，它们会出现在这里。如果不划线，此处会自动隐藏或留空。


---

## 📄 剪藏正文

## The Idea Behind Karpathy’s LLM WikiKarpathy 的 LLM 维基背后的理念

Andrej Karpathy — co-founder of OpenAI, former Tesla AI director, and one of the clearest explainers of machine learning concepts working today — has talked publicly about a deceptively simple idea: your personal notes and documents, organized in plain markdown, can become a knowledge base that an LLM can actually reason over.  
Andrej Karpathy — OpenAI 的联合创始人、前特斯拉 AI 总监，以及当今最清晰的机器学习概念解释者之一 — 公开讨论过一个看似简单但极具启发性的想法：你的个人笔记和文档，如果用纯 markdown 组织起来，可以成为一个 LLM 实际能够推理的知识库。

He calls it an LLM wiki. The concept is straightforward. Instead of scattering knowledge across Notion, Google Docs, browser bookmarks, and sticky notes, you keep everything as structured markdown files. Then you point Claude Code (or any capable coding agent) at that folder and ask it questions. The LLM reads your files, finds what’s relevant, and gives you grounded answers drawn from your own knowledge — not the general internet.  
他称之为 LLM 维基。这个概念很简单。你不是将知识分散在 Notion、Google Docs、浏览器书签和便利贴上，而是将所有内容作为结构化的 markdown 文件保存。然后你将 Claude Code（或任何能够胜任的编程代理）指向那个文件夹，并询问它问题。LLM 读取你的文件，找到相关内容，并为你提供基于你自身知识的可靠答案——而不是来自互联网的通用信息。

This isn’t a product. It’s a workflow pattern. And it’s one of the most practical applications of Claude Code that most people haven’t tried yet.  
这不是一个产品。这是一个工作流程模式。而且它是 Claude Code 最实用的应用之一，大多数人还没有尝试过。

This guide explains how Karpathy’s LLM wiki works, why markdown is the right format for it, and how to get a working version running with Obsidian in about five minutes.  
本指南解释了 Karpathy 的 LLM 维基的工作原理，为什么 Markdown 是适合它的格式，以及如何在五分钟内使用 Obsidian 运行一个可工作的版本。

*Last updated: 2026-05-11 — added related Claude Code workflow links and second-brain comparisons.  
最后更新时间：2026-05-11 — 添加了相关的 Claude 代码工作流链接和第二大脑比较。*

---

## What Makes This Different From a Normal Notes App与普通笔记应用的差异在哪里

Most note-taking apps are built for human reading. You browse, search, click. They’re optimized for you to find things manually.  
大多数笔记应用都是为人类阅读而构建的。你浏览、搜索、点击。它们是为你手动查找信息而优化的。

An LLM wiki is optimized for the model to read on your behalf. That shift changes everything about how you structure information.  
一个 LLM 维基是为模型优化，以便为你阅读。这种转变改变了你如何组织信息的一切。

## Remy is new. 雷米是新的。 The platform isn't. 这个平台不是。

Remy 雷米

Product Manager Agent 产品经理代理

THE PLATFORM 这个平台

200+ models 200 多个模型 1,000+ integrations 1,000 多项集成 Managed DB 管理数据库 Auth 身份验证 Payments 支付 Deploy 部署

▮

BUILT BY MINDSTUDIO 由 MINDSTUDIO 打造

Shipping agent infrastructure since 2021  
自 2021 年以来，货运代理基础设施

Remy is the latest expression of years of platform work.  
雷米是多年来平台工作的最新体现。 Not a hastily wrapped LLM.  
不是匆忙包装的 LLM。

Here’s the core distinction:  
核心区别在于：

- **Traditional notes app**: You remember where something is and navigate to it  
	传统笔记应用：你记得某件事在哪里，然后去查找它
- **LLM wiki**: You describe what you need in plain language, and Claude finds and synthesizes it across your entire knowledge base  
	LLM 维基：你用 plain language 描述你需要什么，Claude 在你的整个知识库中查找并综合信息

The model doesn’t care about your folder hierarchy or tags. It reads text. So plain markdown — which is just text with minimal syntax — is the ideal format. No proprietary encoding, no locked databases, no export friction.  
该模型不关心你的文件夹层次结构或标签。它读取文本。因此纯 Markdown——它只是带有最少语法的文本——是理想的格式。没有专有编码，没有锁定数据库，没有导出摩擦。

Claude Code specifically is well-suited to this because it can read files directly from your local filesystem. You don’t need to paste content into a chat window. You just tell it where your notes live and ask your question.  
Claude Code 特别适合这种情况，因为它可以直接从你的本地文件系统中读取文件。你不需要将内容粘贴到聊天窗口中。你只需要告诉它你的笔记在哪里，然后提出你的问题。

---

## Why Markdown Is the Right Foundation为什么 Markdown 是正确的基石

Before getting into setup, it’s worth understanding why Karpathy’s approach centers on markdown rather than any other format.  
在进入设置之前，了解 Karpathy 的方法为何以 Markdown 为中心而不是其他任何格式，这是有价值的。

### Markdown Is Portable and Future-ProofMarkdown 是可移植且面向未来的

A `.md` file is a text file. It opens in any editor, on any operating system, forever. You’re not dependent on a company staying in business or an app maintaining backward compatibility.  
`.md` 文件是一个文本文件。它可以在任何编辑器中打开，在任何操作系统上，永远如此。你不会依赖于一家公司继续经营或一个应用程序保持向后兼容性。

### LLMs Read Markdown Natively大型语言模型原生支持 Markdown

Models like Claude are trained on enormous amounts of markdown content — GitHub READMEs, documentation sites, forums. The syntax is part of their understanding. Headers, bullet points, code blocks, bold text — Claude interprets all of it as structure, not noise.  
像 Claude 这样的模型在大量的 Markdown 内容上进行训练——GitHub README 文件、文档网站、论坛。语法是它们理解的一部分。标题、项目符号、代码块、粗体文本——Claude 将所有这些都解释为结构，而不是噪音。

### It Forces Clarity 它强迫清晰

Writing in markdown discourages the kind of half-finished, poorly organized notes that accumulate in most people’s knowledge systems. Headers require you to name sections. Lists require you to separate items. The format nudges you toward clarity.  
使用 Markdown 写作会阻止大多数人知识系统中积累的那种半成品、组织不善的笔记。标题要求你命名章节。列表要求你分隔项目。格式促使你走向清晰。

### Plain Text Means No Lock-In纯文本意味着没有锁定

You can sync it with git, open it in VS Code, view it in Obsidian, push it to a private GitHub repo, or read it in a terminal. The knowledge is yours in the most literal sense.  
您可以用 git 同步它，在 VS Code 中打开它，在 Obsidian 中查看它，推送到一个私有的 GitHub 仓库，或者在终端中阅读它。知识在您手中，这是最字面的意思。

---

## How Karpathy’s LLM Wiki Actually WorksKarpathy 的 LLM Wiki 实际上是如何工作的

The architecture is minimal. There are three components:  
架构非常简洁。有三个组件：

**1\. A folder of markdown files** This is your knowledge base. It can contain anything: research notes, meeting summaries, project documentation, book notes, personal reference material, code snippets with explanations.  
1\. 一个 markdown 文件夹 这是您的知识库。它可以包含任何内容：研究笔记、会议纪要、项目文档、书籍笔记、个人参考资料、带解释的代码片段。

**2\. A consistent structure within each file** Good LLM wikis use a consistent internal format — a title, a brief summary, tagged topics, and then the content. The model uses this structure to locate relevant information faster.  
2\. 每个文件内部保持一致的格式 好的 LLM 维基使用一致的内部格式——标题、简短摘要、带标签的主题，然后是内容。模型利用这种结构更快地定位相关信息。

**3\. Claude Code as the query interface** You open a terminal, navigate to your wiki folder, launch Claude Code, and ask it a question. Claude reads the files it needs, synthesizes an answer, and can even update or add notes when you ask it to.  
3\. Claude Code 作为查询界面 你打开终端，导航到你的维基文件夹，启动 Claude Code，并向它提问。Claude 读取它需要的文件，综合出一个答案，甚至可以在你要求时更新或添加笔记。

That’s it. No database. No vector embeddings (though you can add them later). No server. Just files and a capable model.  
就这样。没有数据库。没有向量嵌入（尽管你可以稍后添加）。没有服务器。只有文件和一个强大的模型。

### The Role of Claude CodeClaude 代码的角色

Claude Code is Anthropic’s terminal-based coding agent. Unlike Claude in a browser, Claude Code runs in your local environment and has direct access to your filesystem. It can:  
Claude 代码是 Anthropic 的基于终端的编码代理。与浏览器中的 Claude 不同，Claude 代码在您的本地环境中运行，并可以直接访问您的文件系统。它可以：

- Read specific files or entire directories  
	读取特定文件或整个目录
- Search across files for relevant content  
	在文件中搜索相关内容
- Create new files or update existing ones  
	创建新文件或更新现有文件
- Execute shell commands to search, filter, or organize your notes  
	执行 shell 命令以搜索、筛选或组织您的笔记
![Catch up on Hermes — free 60-minute live workshop](https://i.mscdn.ai/1b7301c0-de42-4e46-b110-e9c55396e7ca/generated-images/2f72d608-9e6a-4ec2-b2f1-5063df20ef36.png?fm=auto&w=1200)

This makes it genuinely useful as a knowledge base interface. You’re not copy-pasting chunks of text into a chat window — the model is working directly with your files. If you want to extend the interaction patterns further, [the Superpowers plugin for Claude Code](https://www.mindstudio.ai/blog/what-is-superpowers-plugin-claude-code) packages reusable skills — including note triage and summarization patterns — that map naturally onto a wiki workflow.  
这使得它作为一个知识库界面非常实用。你不需要将文本片段复制粘贴到聊天窗口中——模型正在直接处理你的文件。如果你想进一步扩展交互模式，Claude Code 的 Superpowers 插件提供了可重用的技能——包括笔记筛选和摘要模式——这些技能自然地映射到维基工作流程上。

---

## Set Up Your LLM Wiki in Obsidian (Step-by-Step)在 Obsidian 中设置你的 LLM 维基（分步指南）

Obsidian is the recommended front-end for this workflow. It’s a local-first markdown editor with a strong plugin ecosystem and a clean interface. Your files stay on your disk — Obsidian is just how you read and write them.  
Obsidian 是这个工作流的推荐前端。它是一个本地优先的 Markdown 编辑器，拥有强大的插件生态系统和简洁的界面。你的文件会保留在你的磁盘上——Obsidian 只是用来读取和编辑它们的方式。

### Step 1: Install Obsidian and Create a Vault第一步：安装 Obsidian 并创建一个仓库

Download Obsidian from [the official Obsidian site](https://obsidian.md/). Create a new vault in a folder you’ll remember — something like `~/wiki` or `~/Documents/llm-wiki`.  
从官方 Obsidian 网站下载 Obsidian。在一个你容易记住的文件夹中创建一个新的保险库——比如 `~/wiki` 或 `~/Documents/llm-wiki` 。

A “vault” in Obsidian is just a folder. Everything in it is plain markdown.  
Obsidian 中的“保险库”只是一个文件夹。里面所有内容都是纯 markdown 格式。

### Step 2: Define a Note Template第二步：定义一个注释模板

Consistency is what makes your wiki queryable. Create a template file at `_templates/note.md`:  
一致性使您的维基可查询。在 `_templates/note.md` 创建一个模板文件：

```markdown
# undefined

**Summary**: One sentence describing this note.
**Tags**: #topic1 #topic2
**Created**: 2026-04-06T00:00:00+00:00
**Last Updated**: 2026-04-06T00:00:00+00:00

---

## Content

Write the main content here.

## Related Notes

- [[Note Title]]
```

You don’t need to follow this exactly. The key is that every note has a summary line and tags. These give Claude quick signals about relevance without reading the full file.  
您不需要完全按照这个格式。关键是每条笔记都有一个摘要行和标签。这些为 Claude 提供了快速的相关性信号，而无需阅读整个文件。

### Step 3: Organize Into Broad Topic Folders步骤 3：组织到广泛的主题文件夹中

Don’t over-engineer this. Start with four or five top-level folders:  
不要过度设计这个。从四个或五个顶层文件夹开始：

```plaintext
wiki/
├── _templates/
├── projects/
├── research/
├── reference/
├── meetings/
└── inbox/
```

The `inbox/` folder is for rough notes that haven’t been organized yet. Claude can help you triage these later.  
`inbox/` 文件夹用于存放尚未整理的草稿笔记。Claude 可以帮助您稍后进行分类整理。

### Step 4: Write Your First Notes步骤 4：编写你的第一条笔记

Migrate whatever knowledge matters most to you. Start with things you look up repeatedly — processes you’ve documented, concepts you’ve researched, decisions you’ve made and why.  
迁移对你最重要的知识。从你最常查找的内容开始——你已经记录的流程、你研究过的概念、你做出的决策以及原因。

Don’t try to import everything at once. The wiki grows most naturally when you add notes as you encounter new information.  
不要试图一次性导入所有内容。当你在遇到新信息时添加笔记，维基最自然地成长。

### Step 5: Install Claude Code步骤 5：安装 Claude Code

You’ll need Node.js installed. Then run:  
您需要安装 Node.js。然后运行：

```bash
npm install -g @anthropic-ai/claude-code
```

Authenticate with your Anthropic account and you’re ready.  
使用您的 Anthropic 账户进行身份验证，您就可以开始使用了。

### Step 6: Query Your Wiki第 6 步：查询您的维基

Open a terminal and navigate to your wiki folder:  
打开终端并导航到您的维基文件夹：

```bash
cd ~/wiki
claude
```

Now ask questions:现在提问：

- *“What notes do I have about machine learning interpretability?”*
- *“Summarize everything in my research folder related to RAG systems.”*
- *“I’m writing a proposal on X — what relevant notes do I have?”*
- *“Find any notes where I mentioned the vendor Acme Corp and summarize the key points.”*

Claude will read through your markdown files, identify what’s relevant, and give you a grounded answer. It’ll cite which files it drew from so you can verify and dig deeper.

If you want a more opinionated walkthrough of this exact pattern — including specific Obsidian plugins and Claude Code commands — [How to build an AI second brain with Claude Code and Obsidian](https://www.mindstudio.ai/blog/build-ai-second-brain-claude-code-obsidian) covers the operational details Karpathy’s high-level idea skips.

---

## Best Practices for a Queryable Knowledge Base

A few structural habits make a significant difference in how well Claude can work with your wiki.

### Write Summaries, Not Just Content

![Hermes, walked through line by line — free 1-hour workshop](https://i.mscdn.ai/1b7301c0-de42-4e46-b110-e9c55396e7ca/generated-images/8edf5cbc-5b63-4999-9079-6aeca2aafd65.png?fm=auto&w=1200)

The one-line summary at the top of each note is surprisingly important. Claude reads it to decide whether the full note is relevant. A good summary costs you ten seconds and saves the model from reading files that don’t apply.

### Use Consistent Terminology

If you write “RAG” in some notes and “retrieval augmented generation” in others, Claude can still connect them — but you’ll get cleaner results if you pick one term and use it consistently. Add a brief alias line if a concept has multiple names.

### Link Notes to Each Other

Obsidian’s `[[wiki links]]` format creates connections between notes. Claude can follow these connections, which means a well-linked wiki gives the model a richer graph to reason over than a flat collection of isolated files. For a deeper look at this same idea applied to large codebases, [Graphify’s knowledge-graph approach for Claude Code](https://www.mindstudio.ai/blog/graphify-claude-code-knowledge-graph-large-codebase-70x) compresses huge repositories into navigable mental models — the same principle that makes a well-linked wiki outperform a flat folder.

### Keep Notes Focused

A 10,000-word catch-all document is harder to query than ten focused 1,000-word notes. If a note is covering multiple distinct topics, split it. The more specific each file, the more precisely Claude can locate and apply it.

### Use a /inbox Pattern for Capture

Don’t let perfect be the enemy of useful. Dump rough notes into `/inbox`, then periodically ask Claude to help you clean them up and move them to the right place:

*“Look at my inbox folder and suggest where each note should be filed and what tags it should get.”*

---

## Advanced: Adding Semantic Search

The basic setup — Claude reading files directly — works well for wikis up to a few hundred notes. At larger scale, you’ll want to add a semantic search layer so Claude can narrow candidates before reading full files.

This is where RAG (Retrieval Augmented Generation) comes in. Tools like [LlamaIndex](https://www.llamaindex.ai/) let you build a vector index over your markdown files, which Claude can query to retrieve the most semantically relevant chunks before synthesizing an answer.

Another path: package the wiki-querying logic as a reusable [Claude Code skill](https://www.mindstudio.ai/blog/5-claude-code-skills-cut-token-costs-70-percent-benchmarked). A well-designed skill can pre-filter notes, summarize subsections, and route queries — cutting the token cost of every question you ask the wiki by a meaningful margin once it grows past a few hundred notes.

For most people starting out, this is overkill. The direct file-reading approach scales further than you’d expect, especially on a focused personal knowledge base. Add semantic search when you notice Claude struggling to find things that you know are in your wiki.  
对于大多数刚开始使用的人来说，这有点过度了。直接的文件读取方法比你想象的更能扩展，尤其是在一个专注的个人知识库上。当你发现 Claude 难以找到你知道存在于你的维基中的东西时，再添加语义搜索。

---

## Where MindStudio Fits This WorkflowMindStudio 如何融入这个工作流程

If you want to take your personal knowledge base further — beyond your local machine, or into something a team can use — MindStudio is worth looking at.  
如果你想让你的个人知识库更进一步——超越你的本地机器，或者变成一个团队可以使用的东西——MindStudio 值得一看。

MindStudio is a no-code platform for building AI agents and workflows. One natural application: wrap your markdown wiki in a MindStudio agent that anyone on your team can query through a clean web interface, without needing to touch Claude Code or a terminal.  
MindStudio 是一个无代码平台，用于构建 AI 代理和工作流。一个自然的用例：将您的 markdown 维基包裹在一个 MindStudio 代理中，您的团队成员可以通过一个干净的 Web 界面进行查询，而无需触摸 Claude Code 或终端。

You can build a knowledge base agent that:  
您可以构建一个知识库代理，该代理可以：

- Accepts natural language questions through a custom UI  
	通过自定义界面接受自然语言问题
- Searches your wiki files (synced to Google Drive, Notion, or any connected storage)  
	搜索您的维基文件（与 Google Drive、Notion 或任何连接的存储同步）
- Returns cited, grounded answers  
	返回引用的、有根据的答案
- Logs queries so you can see what people are looking for — and what your wiki is missing  
	记录查询，以便您可以看到人们在寻找什么——以及您的维基缺少什么
![A free 1-hour Hermes workshop](https://i.mscdn.ai/1b7301c0-de42-4e46-b110-e9c55396e7ca/generated-images/922211b2-4085-4d29-85af-55d6920d46d0.png?fm=auto&w=1200)

MindStudio gives you access to Claude, GPT, Gemini, and 200+ other models out of the box, so you’re not locked into any single provider. And with 1,000+ pre-built integrations, connecting your wiki to Slack, email, or your project management tools takes minutes rather than a full engineering sprint.  
MindStudio 让您可以立即访问 Claude、GPT、Gemini 以及 200 多种其他模型，因此您不必被锁定在任何单一供应商。并且，凭借 1,000 多种预构建的集成，将您的维基连接到 Slack、电子邮件或您的项目管理工具只需几分钟，而不是一个完整的工程冲刺。

If you’re building this kind of knowledge infrastructure for a small team, it’s a much faster path than standing up your own RAG pipeline. You can [try MindStudio free at mindstudio.ai](https://mindstudio.ai/).  
如果你为小团队构建这种知识基础设施，这比自行搭建 RAG 管道要快得多。你可以在 mindstudio.ai 免费试用 MindStudio。

For individual workflows — just you and your local files — Claude Code direct is the simpler approach. For anything shared or team-facing, MindStudio handles the infrastructure so you can focus on the knowledge itself. If you want to take the pattern further and let Claude Code orchestrate multiple knowledge sources at once, [building an agentic operating system on Claude Code](https://www.mindstudio.ai/blog/how-to-build-agentic-operating-system-claude-code) walks through how to layer skills, hooks, and routing on top of a base workflow like this one.

---

## Frequently Asked Questions

### What exactly is Karpathy’s LLM wiki?

It’s a personal knowledge management system built on plain markdown files, designed to be queried by an LLM rather than browsed manually. Andrej Karpathy has advocated for storing notes in a structured, LLM-readable format so that coding agents like Claude Code can answer questions, synthesize information, and help manage the knowledge base directly. The core insight is that organizing information for a model to read is different — and in many ways simpler — than organizing it for human navigation.

### How is this different from just using Notion AI or ChatGPT?

The key difference is that your knowledge lives in files you control, not in a proprietary system. With a local markdown wiki and Claude Code, the model reads your actual files. You’re not uploading data to a third-party knowledge base, and you’re not dependent on one company’s AI staying useful or affordable. You also get much more precise answers because Claude is reading *your* specific notes, not doing a web search or drawing on general training data.  
关键区别在于你的知识存储在你控制的文件中，而不是在专有系统中。通过本地 Markdown 维基和 Claude Code，模型读取你实际的文件。你不会将数据上传到第三方知识库，也不依赖于某家公司的 AI 保持有用或价格合理。你还因为 Claude 正在读取你的特定笔记，而不是进行网络搜索或依赖通用训练数据，从而获得更精确的答案。

### Do I need to know how to code to use Claude Code?我需要知道如何编程才能使用 Claude Code 吗？

No. Claude Code runs in a terminal and you interact with it through natural language. You type questions; it responds and reads your files. The “code” in the name refers to its ability to write and edit code — but for a personal wiki use case, you’re mostly asking questions and getting answers. If you’re comfortable opening a terminal and running one install command, you can use it.  
没有。Claude Code 在终端中运行，您通过自然语言与其交互。您输入问题；它进行响应并读取您的文件。“code”在名称中的含义是指其编写和编辑代码的能力——但对于个人维基使用场景，您主要是在提问并获取答案。如果您能在终端中打开并运行一个安装命令，您就可以使用它。

### How many notes can Claude Code handle at once?Claude Code 一次能处理多少条笔记？

Claude’s context window is large — Claude 3.5 Sonnet supports around 200,000 tokens — which means it can comfortably read tens of thousands of words in a single session. For most personal wikis (up to a few hundred focused notes), this is more than enough. You’ll only need semantic search or RAG if your wiki grows very large, or if you need faster response times on a huge corpus.  
Claude 的上下文窗口很大——Claude 3.5 Sonnet 支持大约 200,000 个 token——这意味着它可以在单次会话中舒适地阅读数万字的文本。对于大多数个人维基（最多几百条专注的笔记），这已经足够了。只有当你的维基规模非常大，或者你需要在庞大的语料库上获得更快的响应时间时，你才需要语义搜索或 RAG。

### Is Obsidian required, or can I use a different editor?Obsidian 是必需的吗，还是我可以使用其他编辑器？

![Wondering what the Hermes hype is about? Free 60-minute primer](https://i.mscdn.ai/1b7301c0-de42-4e46-b110-e9c55396e7ca/generated-images/c8d61682-41d9-44c0-a2fe-5299b2d46f88.png?fm=auto&w=1200)

Obsidian isn’t required. It’s just a convenient front-end for reading and writing markdown files. You could use VS Code, Typora, iA Writer, Zed, Vim, or any text editor. The wiki is just a folder of `.md` files. Obsidian is recommended because its graph view, backlinks, and plugin ecosystem are useful for managing a growing knowledge base — but Claude Code doesn’t care what editor you use.

### Can I use this workflow with other AI models besides Claude?我能使用这个工作流程与其他 AI 模型（除了 Claude）一起使用吗？

Yes. The markdown wiki pattern works with any model that can read files. Claude Code is the most natural interface because it’s built to work directly with your local filesystem. GPT-4 via the OpenAI API, Gemini, or any other capable model can also be pointed at markdown files through similar agent frameworks. Claude tends to perform well for document synthesis tasks, which is why it’s the common recommendation for this use case.

---

## Key Takeaways 关键要点

- Karpathy’s LLM wiki is a simple pattern: structured markdown files, queried by Claude Code through natural language
- Plain markdown is the right format because it’s portable, future-proof, and something LLMs read natively
- Obsidian is the best front-end for managing the files — your data stays local and file-based
- Claude Code connects to your local filesystem directly, no copy-pasting required
- A summary line and consistent tags on each note dramatically improve query quality
- For team-facing or scaled knowledge bases, MindStudio can wrap the same concept in a shareable, no-code agent with a proper UI

The best knowledge management system is one you’ll actually use. A folder of markdown files is about as low-friction as it gets — and pointing Claude at it takes five minutes. Start small, keep notes focused, and let the system grow with you.