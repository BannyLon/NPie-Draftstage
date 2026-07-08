---
type: inbox
status: pending
标题：: LLM Knowledge Bases
链接：: https://x.com/karpathy/status/2039805659525644595
来源：: X (formerly Twitter)
剪藏时间：: 2026-06-25 17:47
网页摘要：: 在嗯哌，看懂 AI，看清未来！陪你在AI时代重塑生产力
---
## 🤖 AI 智能解析
> [!brain] 核心摘要
> Andrej Karpathy 分享了他最近使用 LLM 构建个人知识库的有效方法：通过将源文档索引到 raw/ 目录，让 LLM 逐步编译成以 Markdown 文件维基，包括摘要、反向链接、概念分类和文章链接，并使用 Obsidian 作为 IDE 前端查看原始数据、编译后维基和可视化结果，由于 LLM 负责编写与维护，用户很少直接编辑，当维基足够大时可向 LLM 代理提出复杂问题而无需复杂的 RAG，LLM 能自动维护索引文件和总结，输出形式包括 Markdown 文件、幻灯片或 matplotlib 图像并可归档回维基，同时还可对维基进行健康检查以发现不一致、填充缺失数据和寻找新文章候选连接，用户还开发了额外工具如小型搜索引擎，并考虑合成数据生成与微调让 LLM 将数据融入权重而非仅靠上下文窗口，整体流程是收集原始数据由 LLM 编译为. md 维基再通过 CLI 操作进行问答与增量增强，所有内容在 Obsidian 中展示，用户认为这为创新产品留下空间。

> [!list] 关键要点 (Key Facts)
> > - 方法流程：将源文档索引到 raw/，让 LLM 逐步编译成包含摘要、反向链接、概念文章和链接的. md 格式维基，并使用 Obsidian 作为前端。

> - LLM 主导：LLM 负责编写、维护和增强维基的所有数据，用户很少直接编辑，并可进行健康检查如发现不一致和填充缺失数据。

> - 输出与应用：LLM 可对维基进行 Q&A 输出 Markdown、幻灯片或 matplotlib 图像，输出可归档回维基，还支持开发额外工具如小型搜索引擎，并考虑合成数据生成与微调。

---

## 📌 我的网页划线
> [!tip] 提示
> 如果你在网页上用鼠标选中文本并高亮，它们会出现在这里。如果不划线，此处会自动隐藏或留空。


---

## 📄 剪藏正文

[Andrej Karpathy](https://x.com/karpathy)[@karpathy](https://x.com/karpathy)

LLM Knowledge Bases  
LLM 知识库  
  
Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge (stored as markdown and images). The latest LLMs are quite good at it. So:  
最近我发现一个非常有用的方法：使用大型语言模型（LLMs）来构建关于各种研究兴趣主题的个人知识库。通过这种方式，我最近很大一部分的 token 吞吐量不再用于操作代码，而是用于操作知识（以 markdown 和图像形式存储）。最新的 LLMs 在这方面表现相当出色。所以：  
  
Data ingest: I index source documents (articles, papers, repos, datasets, images, etc.) into a raw/ directory, then I use an LLM to incrementally "compile" a wiki, which is just a collection of.md files in a directory structure. The wiki includes summaries of all the data in raw/, backlinks, and then it categorizes data into concepts, writes articles for them, and links them all. To convert web articles into.md files I like to use the Obsidian Web Clipper extension, and then I also use a hotkey to download all the related images to local so that my LLM can easily reference them.  
数据摄取： 我将源文档（文章、论文、代码库、数据集、图片等）索引到 raw/ 目录中，然后使用一个大型语言模型（LLM）逐步“编译”一个维基，它只是一个目录结构中的.md 文件集合。这个维基包含 raw/ 中所有数据的摘要、反向链接，然后它将数据分类到不同的概念中，为它们撰写文章，并将它们全部链接起来。为了将网页文章转换为.md 文件，我喜欢使用 Obsidian Web Clipper 扩展，然后我还使用快捷键将所有相关图片下载到本地，这样我的 LLM 就可以轻松地引用它们。  
  
IDE: I use Obsidian as the IDE "frontend" where I can view the raw data, the the compiled wiki, and the derived visualizations. Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly. I've played with a few Obsidian plugins to render and view data in other ways (e.g. Marp for slides).  
IDE： 我使用 Obsidian 作为 IDE 的“前端”，在那里我可以查看原始数据、编译后的维基以及派生的可视化。重要的是要注意，LLM 编写和维护维基的所有数据，我很少直接接触它。我尝试过几个 Obsidian 插件，以其他方式（例如 Marp 用于幻灯片）来渲染和查看数据。  
  
Q&A: Where things get interesting is that once your wiki is big enough (e.g. mine on some recent research is ~100 articles and ~400K words), you can ask your LLM agent all kinds of complex questions against the wiki, and it will go off, research the answers, etc. I thought I had to reach for fancy RAG, but the LLM has been pretty good about auto-maintaining index files and brief summaries of all the documents and it reads all the important related data fairly easily at this ~small scale.  
Q&A： 有趣之处在于，一旦你的维基足够大（例如我最近关于某项研究的维基有 ~1001 篇文章和 ~40 万字），你就可以向你的 LLM 代理提出各种复杂的问题，它就会去研究答案等。我以为我需要使用复杂的 RAG，但 LLM 在自动维护索引文件和所有文档的简要摘要方面表现得相当好，并且在这个 ~小规模上它能 fairly easily 地读取所有重要的相关数据。  
  
Output: Instead of getting answers in text/terminal, I like to have it render markdown files for me, or slide shows (Marp format), or matplotlib images, all of which I then view again in Obsidian. You can imagine many other visual output formats depending on the query. Often, I end up "filing" the outputs back into the wiki to enhance it for further queries. So my own explorations and queries always "add up" in the knowledge base.  
Output: 与其在文本/终端中获取答案，我更喜欢让它渲染 Markdown 文件给我，或者幻灯片（Marp 格式），或者 matplotlib 图像，我之后会在 Obsidian 中再次查看它们。你可以想象根据查询有很多其他可视化输出格式。通常，我会把输出“归档”回维基中以增强它，以便进行进一步的查询。所以我的探索和查询总是“累积”在知识库中。  
  
Linting: I've run some LLM "health checks" over the wiki to e.g. find inconsistent data, impute missing data (with web searchers), find interesting connections for new article candidates, etc., to incrementally clean up the wiki and enhance its overall data integrity. The LLMs are quite good at suggesting further questions to ask and look into.  
代码检查： 我运行了一些 LLM"健康检查"在维基上，例如找出不一致的数据，用网络搜索器填充缺失数据，寻找有趣连接作为新文章候选等，以逐步清理维基并提高其整体数据完整性。LLM 在提出进一步的问题去询问和研究方面相当不错。  
  
Extra tools: I find myself developing additional tools to process the data, e.g. I vibe coded a small and naive search engine over the wiki, which I both use directly (in a web ui), but more often I want to hand it off to an LLM via CLI as a tool for larger queries.  
额外工具： 我发现自己在开发额外的工具来处理数据，例如我 vibe 编写了一个小型且简单的维基搜索引擎，我既直接使用它（在网页界面中），但更经常我想通过 CLI 将其交给 LLM 作为更大查询的工具。  
  
Further explorations: As the repo grows, the natural desire is to also think about synthetic data generation + finetuning to have your LLM "know" the data in its weights instead of just context windows.  
进一步的探索： 随着仓库的增长，自然地也想考虑合成数据生成 + 微调，让你的 LLM "知道" 数据在其权重中，而不是仅仅在上下文窗口中。  
  
TLDR: raw data from a given number of sources is collected, then compiled by an LLM into a.md wiki, then operated on by various CLIs by the LLM to do Q&A and to incrementally enhance the wiki, and all of it viewable in Obsidian. You rarely ever write or edit the wiki manually, it's the domain of the LLM. I think there is room here for an incredible new product instead of a hacky collection of scripts.  
TLDR：从给定数量的源收集原始数据，然后由大型语言模型（LLM）将其编译成.md 格式的维基，接着由 LLM 通过各种 CLI 进行操作，以进行问答和逐步增强维基，所有内容都可以在 Obsidian 中查看。你很少需要手动编写或编辑维基，这是 LLM 的领域。我认为这里有机会开发一款令人难以置信的新产品，而不是一堆蹩脚的脚本。