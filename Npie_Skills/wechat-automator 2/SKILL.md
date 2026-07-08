---
name: wechat-automator
description: 一站式内容资产化引擎：默认对内容进行深度优化（契合公众号阅读场景），精排版渲染，一键上传草稿箱。当用户提到"推文"、"公众号"、"排版"、"发布"、"草稿"、或任何将内容转化为公众号图文的意图时，必须调用此技能。
version: 1.7.0
---

# 微信公众号内容资产化引擎 (WeChat Automator)

## 一句话定义

**把短期流量（视频/笔记/碎片资料），转化为长期内容复利（可搜索、可收藏、可反复阅读的图文资产）。**

---

## 触发条件 (Trigger Rules)

以下任一条件满足时，**必须**激活此技能：

1. **关键词触发**：用户消息包含以下任一关键词组合：
   - 「推文」「公众号」「排版」「发布」「草稿」「群发」「图文」
   - 「wechat」「weixin」「mp.weixin」
   - 「视频脚本」+「转/整理/发/变成」→公众号意涵
   - 「笔记」+「排版/发布/推文」
2. **文件引用触发**：用户引用了 `.md` / `.writings.md` / `.txt` 文件，并提到「发」「传」「推送」「转成图文」等动作词。
3. **路径指令触发**：
   - `wechat-automator:full(file_path)` — 完整链路：输入→草稿箱
   - `wechat-automator:format(file_path)` — 仅排版预览，不上传
   - `wechat-automator:upload_cover(path)` — 仅上传封面图
4. **上下文推断触发**：刚完成 oral-stylizer 处理，用户自然过渡到排版发布。

**🔴 强制规则：一旦触发，必须用 `Skill` 工具加载本 skill，并严格按照 skill 内定义的五阶段流水线执行。严禁绕过 skill 自行编写脚本、手写 HTML、或直接用 `requests` 调 API。**

**反触发**：纯技术咨询（「公众号 API 怎么调」）不激活，用通用知识回答。

---

## 默认行为与内容优化豁免

### 核心原则：默认深度优化，显式声明豁免

**默认行为**：对用户提供的任何内容，自动执行阶段 ①②（内容脱水 + 结构重组），使内容契合微信公众号读者的阅读习惯——包括但不限于：重构开头钩子、调整段落节奏、优化小标题、强化结尾 CTA。

**豁免规则**：仅当用户消息中**明确包含**以下任一关键词组合时，才跳过阶段 ①② 的内容修改，严格保留原文：

| 豁免关键词 | 示例 |
|-----------|------|
| 「不要修改内容」「不做任何修改」「不要改动」 | 「排版发公众号，**不要改动**原文任何一个字」 |
| 「严格按原文」「原封不动」「一字不改」 | 「**严格按原文**排版，发布到草稿箱」 |
| 「不增不减」「保留原文」「直接排版」 | 「**不增不减**，直接排版」 |
| 「仅排版」「只排版」「纯排版」 | 「**仅排版**，不需优化内容」 |

**注意**：豁免的是阶段 ①② 的**内容改写**，阶段 ③④ 的视觉增强和排版渲染始终执行。即使用户要求「不修改内容」，仍然要执行：卡片化、金句模块提取、数据可视化、配色排版。

### 判断流程

```
用户请求 → 引用的文件是 .html？
  ├─ 是 → 兼容性扫描：有 <style>？有 <div>？有 class？
  │        ├─ 全部干净 → 直达 ⑤ 上传（跳过 ①②③④）
  │        └─ 有问题   → 告知用户问题数量，询问是否自动修复后再上传
  └─ 否 → 检查是否包含豁免关键词？
           ├─ 是 → 跳过 ①②，进入 ③ 视觉增强 → ④ 排版渲染 → ⑤ 上传
           └─ 否 → 执行阶段 ①② → 🔴 暂停，输出预览给用户确认
                     ├─ 用户确认 → 继续 ③ 视觉增强 → ④ 排版渲染 → ⑤ 上传
                     └─ 用户要求修改 → 修改后再次预览，直到确认
```

**🔴 阶段 ①② 确认门禁（强制）**：执行完内容脱水 + 结构重组后，**必须暂停**，将优化后的 Markdown 内容输出给用户预览，等待用户明确确认（「确认」「可以」「继续」等）后，才能继续执行阶段 ③④⑤。禁止跳过此门禁直接完成全流程。

**HTML 兼容性扫描标准**（干净 HTML 的定义）：
- 无 `<style>` 标签
- 无 `class` 属性
- 无 `<div>` 元素
- 无可检测的 `linear-gradient`

四条全部满足 → 直达 ⑤。任一不满足 → 告知用户「这个 HTML 有 X 个 div / Y 个 style 标签，微信会丢格式，要我先修复吗？」

---

## 工作流总览（v1.7.0）

```
三阶段管线：
┌──────────┐    ┌──────────────┐    ┌──────────┐
│ ⓪ 内容优化 │ → │ ① 排版渲染    │ → │ ② 一键发布 │
│ 脱水+去AI │    │ 推荐+预览+选择 │    │ 草稿箱    │
│ 🔴暂停确认 │    │ 🔴暂停确认     │    │ 自动完成  │
└──────────┘    └──────────────┘    └──────────┘

详细流程：
  输入内容
    ↓
  ⓪.1 内容脱水（去冗余/提论点/压密度）
  ⓪.2 结构重组（钩子开头+正文骨架+CTA结尾）
  ⓪.3 去AI味（humanizer-zh 审阅）
    ↓
  🔴 暂停 → 输出优化后内容 → 等待用户确认
    ↓
  ①.1 深度理解文章内容 → 分析视觉结构
  ①.2 内容匹配分析 → 推荐最佳排版系统
  ①.3 生成预览网页 → 浏览器并排对比 6 套系统
    ↓
  🔴 暂停 → 用户选择排版系统（预设名/自定义组合/自定义颜色）
    ↓
  ①.4 build_inline.py --theme <选定> → inline HTML
    ↓
  ② upload.py → 上传头图+封面 → 创建草稿
    ↓
  ✅ 草稿 media_id → 用户去后台预览群发
```

### 确认门禁（两处强制暂停）

1. **内容确认**：阶段⓪ 完成后，输出优化后的 Markdown，等用户确认
2. **排版确认**：阶段① 预览网页打开后，等用户选定排版系统

### 豁免规则

- 用户说「不要修改内容」「一字不改」「仅排版」→ 跳过 ⓪，直接进入 ①
- 用户引用的文件是干净 HTML → 跳过 ⓪①，直达 ②

---

## 阶段 ⓪：内容优化（Content Optimization）

**目标**：输入内容 → 深度优化 → 去 AI 味 → 用户确认。

### ⓪.1 内容脱水

1. **去冗余**：删除重复论述、口语填充句
2. **提论点**：每段提炼 1 句可独立传播的核心观点
3. **压密度**：信息密度提升 30-50%
4. **保人味**：保留作者标志性表达（Banny 的「Vibe Coding」「Agentic Workflow」等）

### ⓪.2 结构重组

- **钩子开头**：提取最反直觉的 1 句话前置，或用 2-3 句制造信息落差
- **正文架构**：根据内容类型选择骨架（教程→问题原理步骤/观点→现象分析本质/案例→背景决策方法论/清单→总览逐条展开）
- **H2 控制**：3-5 个板块，标题要具体（「问题是什么」而非「关于 XX 的讨论」）
- **CTA 结尾**：给读者一个具体的下一步

### ⓪.3 去 AI 味

调用 `humanizer-zh` 审阅优化后的全文，去除 AI 写作特征（夸大的象征意义、宣传性语言、三段式法则、AI 词汇等）。

### ⓪.4 确认输出

**🔴 必须暂停**。将优化后的 Markdown 内容输出给用户预览，等待明确确认后才能继续。

---

## 阶段 ①：排版渲染（Layout & Rendering）

**目标**：深度理解文章 → 推荐排版系统 → 预览对比 → 用户选择 → 渲染 HTML。

### ①.1 深度理解 → 推荐

1. 阅读优化后的文章，理解内容类型、情感基调、目标读者
2. 调用 `recommend()` 做关键词匹配分析，得出 6 套系统的分数排名
3. 结合内容理解和关键词分数，向用户说明推荐理由

### ①.2 生成预览网页

```bash
python3 scripts/preview_themes.py output/article-class-html.html --open
```

自动提取文章代表性片段，用全部 6 套排版系统渲染，生成对比页并在浏览器打开。

每张卡片标注：📐 布局名 + 🎨 配色名 + 实际渲染效果。推荐项 ⭐ 高亮。

### ①.3 用户选择

**🔴 必须暂停等待**。用户可回复：

- 预设名：`teal` `navy` `forest` `plum` `slate` `amber`
- 自由组合：`classic:teal-gold` `workshop:navy-coral`
- 自定义颜色：`#e63946`
- 「用推荐的」→ 分数最高项

### ①.4 渲染

```bash
python3 scripts/build_inline.py output/article-class-html.html output/article-inline.html --theme <选定>
```

### ①.5 HTML 生成流程

**Step 1**：根据选定的排版系统，用其专属组件库编写 class-based HTML
**Step 2**：运行 `build_inline.py --theme` 转换为 inline style HTML
**Step 3**：验证（零 style/div/class/linear-gradient/letter-spacing）

### ①.6 排版质量检查

- [ ] 全文无 `<style>`、`class=`、`<div>`、`linear-gradient`、`letter-spacing`
- [ ] 正文行高 ≥ 1.8，字号 ≥ 15px
- [ ] H2 视觉层级正确，关键观点用金句/强调模块包裹
- [ ] CTA 后有底部留白（≥32px）
- [ ] 颜色来自配色色板，全文主色一致
- [ ] 头图位和配图位已标记（由 upload.py 阶段③自动注入）

---

## 微信排版技术规范（Typography & Rendering Reference）

**目标**：无论选择哪套排版系统，最终输出都遵循以下技术规范。

### 4.1 🔴 微信 CSS 核心规则：禁止 `<style>` + 禁止 `<div>`

**两项关键发现**（基于生产环境实测验证）：

| 规则 | 后果 | 解决方案 |
|------|------|---------|
| `<style>` 标签 | ❌ 微信**完全删除** | 所有样式写入 `style=""` 内联属性 |
| `class` 属性 | ❌ 微信**完全剥离** | 不依赖 class 选择器 |
| `<div>` 元素 | ❌ 微信**全部转为裸 `<p>`**，丢失所有样式 | **零 div**：用 `<section>`/`<p>`/`<blockquote>`/`<table>` 替代 |
| `linear-gradient` | ❌ 微信删除 | 用纯色 `background-color` 替代 |

**唯一可靠的样式方式：`style=""` 内联属性 + 零 div + 语义化 HTML 元素。**

### 4.2 微信排版硬约束

- ❌ 禁止 `<style>` 标签（微信直接删除）
- ❌ 禁止 `<div>` 元素（微信转为裸 `<p>`，样式全部丢失）
- ❌ 禁止 `class` 属性（微信直接删除）
- ❌ 禁止外部 CSS 文件、外部字体、JavaScript
- ❌ 禁止 `position: fixed/absolute/sticky`
- ❌ 禁止 `flex` 和 `grid` 布局（微信会剥离）
- ❌ 禁止 `linear-gradient`（微信会删除，改用纯色 `background-color`）
- ❌ 禁止 `<iframe>`、`<form>`、`<input>`
- ⚠️ **`<blockquote>` 有隐性 300 字限制**：微信编辑器对单次引用内容超过 300 字会自动插入「引用字数:XX/300」警告。超过 300 字的引用内容（如 Prompt 全文、长文摘录等）必须改用 `<section>` + `border-left` 样式替代
- ✅ **所有样式写在每个元素的 `style=""` 属性中**
- ✅ **用语义元素替代 div**：`<section>` 做容器、`<blockquote>` 做强调块（≤300字）、`<section>` + 左边框做超长引用（>300字）、`<table>` 做数据对比、`<p>` 做卡片
- ✅ 布局基于 `block`/`inline-block`/`table` + `margin`/`padding`
- ✅ 背景色使用纯色（`background-color`），禁用渐变
- ✅ 图片 src 必须是微信 CDN URL（`mmbiz.qpic.cn` 域名）
- ✅ 容器最大宽度 `677px`

**Div → 语义元素映射表（关键！所有 `<div>` 必须转换）：**

| 原始 div 用途 | 替换元素 | 示例 |
|-------------|---------|------|
| 页面容器 | `<section style="...">` | `<section style="margin:0;padding:0 16px 0;...">` |
| 元信息标签 | `<span style="display:inline-block;...">` 包在 `<p>` 中 | `<p style="text-align:center;"><span style="...">深度解析</span></p>` |
| 开篇大数字 | `<p>` + `<strong>` | `<p style="text-align:center;"><strong style="font-size:56px;">9,500 ★</strong></p>` |
| 金句模块 | `<blockquote style="...">`（不设左边框） | `<blockquote style="background-color:#d4edf5;border-radius:12px;text-align:center;">` |
| 强调模块 | `<blockquote style="...">`（带完整边框） | `<blockquote style="background-color:#f7fafc;border:1px solid #e0e7ef;">` |
| 卡片列表 wrapper | 直接删除，子项用 `<p>` | |
| 卡片项 | `<p style="...">`（带背景+边框+圆角） | `<p style="background-color:#fafbfc;border:1px solid #e8ecf1;border-radius:8px;">` |
| 数据双栏 | `<table>` + `<td style="width:50%">` | |
| CTA 底部 | `<blockquote style="...">`（不设左边框） | `<blockquote style="margin-top:44px;background-color:#d4edf5;border-radius:14px;">` |
| 编辑注记 | `<p style="...">`（左侧灰色细线） | `<p style="border-left:2px solid #dce3ea;color:#8a9aaa;font-style:italic;">` |
| 超长引用（>300字） | `<section style="...">`（左边框 + 略小字号，视觉等效 blockquote 但不触发微信 300 字限制） | `<section style="border-left:3px solid #0d7377;margin:16px 0;padding:4px 0 4px 18px;"><p style="font-size:14px;color:#4a5a6a;">...</p></section>` |

### 4.3 6 套异构排版系统（v1.6.0）

每套排版系统拥有**独立的组件库、HTML 结构和视觉语言**，不是同一骨架换 CSS。

#### 排版系统一览

| 系统 | 设计理念 | H2 特征 | 独有组件 | 参考 |
|------|---------|---------|---------|------|
| `classic` 经典左线 | 左粗线分区，结构清晰 | 左蓝条+浅底 | `.golden-quote` `.card-item` `.highlight-box` | 咨询报告 |
| `cardflow` 卡片流 | 每段独立成卡，模块化 | 深色顶栏（卡片标题） | `.section-card` `.info-card` `.data-badge` | Notion |
| `editorial` 杂志流 | 大标题+引题+戏剧化引用 | 居中+上下装饰线 | `.lead` `.ornament-divider` `.image-frame` | The Atlantic |
| `guide` 手册流 | 步骤编号+提示框+对比 | 最大号无装饰 | `.step-num` `.tip-box` `.warn-box` `.checklist-item` `.before-after` | 操作指南 |
| `letter` 书信流 | 日期+问候+署名，极简 | 只比正文略大 | `.dateline` `.greeting` `.sign-off` `.signature` `.postscript` | Substack |
| `workshop` 极客流 | 深色实验台+Prompt卡+工具徽章 | 深底白字，等宽感 | `.prompt-card` `.tool-badge` `.workflow-step` `.wf-step-num` | 开发者笔记 |

#### 关键区别

同一篇文章用不同排版系统，**golden-quote（金句）** 的渲染完全不同：
- `classic`：圆角蓝底居中卡片
- `cardflow`：卡片底部横幅
- `editorial`：上下装饰线+大号居中
- `guide`：深色满底反白块
- `letter`：无底无边框，纯文字加大加粗
- `workshop`：深色实验台+对比色文字

#### 5 套多对比色配色方案（决定颜色组合）

| 配色名 | 主色 | 对比色 | 气质 |
|--------|------|--------|------|
| `teal-gold` | `#0d7377` 青蓝 | `#c8940a` 暖金 | 理性中带温度 |
| `navy-coral` | `#2c3e6b` 深蓝 | `#d4685c` 珊瑚 | 专业不过分严肃 |
| `forest-amber` | `#2d6a4f` 深绿 | `#d4923a` 琥珀 | 自然沉稳有生机 |
| `plum-sage` | `#7c3a8c` 梅紫 | `#6b8b7a` 灰绿 | 文艺不张扬 |
| `slate-rose` | `#4a5568` 岩灰 | `#c57080` 玫瑰 | 克制中带柔软 |

每个配色包含 16 个色值 token（primary/contrast/bg_light/bg_warm/bg_dark/text_on_dark/text_dark/text_body/text_muted/border/border_light/card_bg/code_bg/code_color/white/body_bg），确保全文色彩协调。

#### 6 套预设主题组合

| 预设名 | 布局 | 配色 | 适用内容 |
|--------|------|------|---------|
| `teal` | classic 经典左线 | teal-gold 青蓝金 | 通用深度分析 |
| `navy` | editorial 杂志流 | navy-coral 深蓝珊瑚 | 商业/行业评论 |
| `forest` | guide 手册流 | forest-amber 森语琥珀 | 教程/操作指南 |
| `plum` | cardflow 卡片流 | plum-sage 梅紫灰绿 | 产品/工具介绍 |
| `slate` | letter 书信流 | slate-rose 岩灰玫瑰 | 个人随笔/故事 |
| `amber` | workshop 极客流 | forest-amber 森语琥珀 | 技术/AI/编程 |

#### 使用方式

```bash
# 预设组合
python3 scripts/build_inline.py in.html out.html --theme navy

# 显式指定布局和配色
python3 scripts/build_inline.py in.html out.html --layout workshop --palette teal-gold

# 自定义主色（默认 classic 布局，自动推导配色）
python3 scripts/build_inline.py in.html out.html --theme "#e63946"
```

---

### 4.3.5 主题推荐与可视化预览（v1.3.0）🔴 强制交互节点

在运行 `build_inline.py` 之前，**必须**执行以下交互流程：

#### 步骤 A：内容分析 → 自动推荐

调用 `recommend_theme()` 分析文章文本，按关键词匹配度评分。每个主题内置一组关键词：

| 主题 | 匹配关键词 | 适合内容类型 |
|------|-----------|-------------|
| `navy` 靛蓝 | 商业、行业、市场、数据、报告、战略、投资、利润、竞争 | 商业分析、行业评论 |
| `forest` 深绿 | 教程、步骤、操作、配置、代码、实战、指南、工具、方法 | 技术教程、操作指南 |
| `amber` 暖金 | 我、经历、感受、故事、碎碎念、随笔、生活、日常 | 个人随笔、经验分享 |
| `teal` 青蓝 | 分析、深度、观点、评论、趋势、解读、思考、本质 | 深度分析、通用评论 |
| `plum` 梅紫 | 创意、设计、艺术、文艺、审美、灵感、创作、风格 | 创意输出、文艺评论 |

#### 步骤 B：生成可视化预览网页

```bash
python3 scripts/preview_themes.py output/article-class-html.html --open
```

该脚本自动：
1. 从 class HTML 中提取代表性片段（开篇 + 首个 H2 板块）
2. 用全部 6 套排版系统渲染同一段内容
3. 生成深色主题对比页 `output/theme-preview.html`
4. 自动在浏览器中打开

预览页包含：
- 📊 **评分图例**：显示每个主题的匹配分数（降序）
- 🎨 **5 列并排卡片**：每个主题在实际文章片段上的渲染效果
- ⭐ **推荐标记**：得分最高的 2 个主题高亮显示（金色边框 + 推荐徽章）
- 💡 **操作提示**：底部提示用户如何选择

#### 步骤 C：用户选择

预览页打开后，**必须暂停等待用户选择**。用户可回复：
- 主题名：`navy`、`amber`、`forest`、`teal`、`plum`
- 自定义颜色：`#e63946`
- 默认确认：「就用推荐的」→ 使用得分最高的主题

#### 步骤 D：进入 build_inline.py

用户确认后，将选定主题传入：
```bash
python3 scripts/build_inline.py output/article-class-html.html output/article-inline.html --theme <选定主题>
```

---

### 4.4 嵌套上下文特殊处理

某些元素在特定父容器内需要覆盖默认样式：

| 父容器 | 子元素 | 特殊处理 |
|--------|--------|---------|
| `<blockquote>` | `<p>` | `color:#4a5a6a;font-size:14px;`（覆盖默认 p 的 `color:#3f3f3f`） |
| `<pre>` | `<code>` | 去掉 `background-color` 和 `color`（继承 pre 的深色主题） |
| `.golden-quote` | `<p>` | `color:#0d7377;font-weight:700;text-align:center;` |
| `.highlight-box` | `<strong>` | `color:#0d7377;`（覆盖默认 strong 的 `color:#212121`） |
| `.cta-footer` | `<p>` | `color:#0d7377;font-weight:500;text-align:center;font-size:14px;` |

### 4.5 HTML 生成流程

**Step 0**：主题推荐与预览（v1.3.0 🔴 强制交互）
- 用 `recommend_theme()` 分析文章内容 → 自动推荐最匹配的主题
- 运行 `preview_themes.py --open` → 在浏览器中并排展示 5 套主题的实际渲染效果
- **暂停等待用户选择**（主题名 / 自定义颜色 / 「用推荐的」）
- 将选定 `--theme <name|#RRGGBB>` 传给 `build_inline.py`

**Step 1**：生成 class-based HTML（便于结构可读性）
```html
<blockquote class="golden-quote"><p>万物皆可蒸馏</p></blockquote>
```
⚠️ 必须使用语义元素（`<p>`, `<blockquote>`, `<h2>`, `<h3>`, `<section>`, `<code>`, `<hr>`, `<strong>`），严禁 `<div>`。**🔴 禁止 `<pre>` 标签**（微信不支持，换行全部丢失，参见铁律 7）。格式化文本用 `<section>` + `white-space:pre-wrap` + `<br>` 替代。

⚠️ `<code>` 内如需展示 HTML 标签（如 `<style>`），必须写 `&lt;style&gt;`，不要写裸 `<style>`。

⚠️ **头图（v1.3.0）**：class-based HTML 中**不要写头图 `<img>`**。头图由 `upload.py` 自动上传 `img/header_image.png` 并在阶段⑤注入正文顶部。

**Step 2**：用 `build_inline.py` 将 class 映射转换为 inline style
```bash
python3 scripts/build_inline.py output/article-class-html.html output/article-inline.html --theme teal
```
```python
# 🔴 关键：必须设置 convert_charrefs=False
# 否则 HTMLParser 会把 &lt; &gt; 转成 < >，导致 <code> 内的标签被当作真标签吃掉内容
parser = HTMLParser(convert_charrefs=False)
# 移除所有 class 属性，注入对应的 style 属性（颜色来自主题色板）
```

**Step 3**：后处理嵌套上下文冲突（blockquote p、pre code、golden-quote p、cta-footer p 等）
⚠️ 嵌套覆盖必须追踪父级 class 名，不能只追踪 tag 名。例如 `golden-quote` 下的 `<p>` 和普通 `blockquote` 下的 `<p>` 需要不同的覆盖样式。

**Step 4**：输出纯 body 片段 HTML（仅 inner content，不含 `<html>`, `<head>`, `<body>` 标签），所有样式通过 `style=""` 内联，全文无 `<style>` 标签、无 `class` 属性、无 `<div>` 元素。

**Step 5**（v1.3.0）：运行 `upload.py` 完成头图注入 + 底部留白 + 封面上传 + 草稿创建
```bash
python3 scripts/upload.py --token TOKEN --html output/article-inline.html --title "标题" --author "嗯哌" --digest "摘要"
```
upload.py 自动执行：上传 `img/header_image.png` → 注入 `<img>` 到正文顶部 → 底部注入留白 `<p>` → 上传 `img/cover.png` 做封面 → 创建草稿

### 4.6 排版质量检查清单

- [ ] 全文无 `<style>` 标签
- [ ] 全文无 `class` 属性
- [ ] 所有元素样式通过 `style=""` 内联
- [ ] 全文无 `linear-gradient`（已替换为纯色 `background-color`）
- [ ] 全文无 `letter-spacing`
- [ ] 正文行高 ≥ `1.8`，字号 ≥ 15px
- [ ] 在 375px 宽视口下无横向滚动
- [ ] H2 ≤ 19px，视觉层级正确（H2 > H3 > 正文 > 辅助文字）
- [ ] 关键观点使用金句模块或强调模块包裹
- [ ] 文章底部有 CTA 模块
- [ ] CTA 之后有底部留白（≥32px 空行，便于追加底部信息）
- [ ] blockquote / golden-quote / cta-footer 内子元素样式已做嵌套覆盖
- [ ] class-based HTML 中不含头图 `<img>`（由 upload.py 阶段⑤自动注入）
- [ ] 颜色来自主题色板，全文主色一致（v1.3.0）

---

## 阶段 ②：一键发布（Publish）

**目标**：排版完成 → 推送到公众号草稿箱，用户打开后台即可预览和群发。

### 5.1 凭据获取

按以下顺序查找微信 API 凭据：

1. **环境变量**：`WEIXIN_APPID` / `WEIXIN_APPSECRET` 或 `WECHAT_APPID` / `WECHAT_APPSECRET`
2. **会话上下文**：如果用户在本轮对话中已提供过，直接复用（不在日志中明文输出）
3. **主动询问**：以上均未找到时，向用户询问 AppID 和 AppSecret。提示路径：公众号后台 → 开发 → 基本配置

凭据仅在当前会话内存缓存，不写入任何文件。

### 5.2 获取 Access Token

```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
```
- 有效期 7200 秒，会话内存缓存复用
- 失败重试 1 次，仍失败则中止并报告错误

### 5.3 封面处理

**`thumb_media_id` 为必填字段**。封面图获取 / 生成优先级：

1. **`img/cover.png`**（v1.3.0 默认）：skill 根目录下预置封面图，直接上传到微信素材库
2. 用户显式指定的图片路径/URL → 上传到微信素材库
3. 文章内第一张 `<img>` 的 src（需已是 `mmbiz.qpic.cn` URL）
4. **自动生成封面图**（fallback）：用 Python 内置库生成品牌色纯色 PNG，1080×1080px → 上传
5. 以上均失败 → 报告错误，不上传空封面

本地上传封面：
```
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=image
```
成功返回 `media_id` 和微信 CDN URL（`mmbiz.qpic.cn`）。将 URL 回填到正文 `<img>` 标签中。

**头图自动注入**（v1.3.0）：`upload.py` 会自动上传 `img/header_image.png` 到微信素材库，获取 CDN URL，并注入到正文 HTML 最顶部。class-based HTML 中**不需要**手写头图 `<img>`。

**封面自动生成代码模板**：
```python
import struct, zlib

def create_cover_png(w=1080, h=1080):
    """生成品牌色纯色 PNG"""
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc
    
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            raw += struct.pack('BBB', 13, 115, 119)  # #0d7377
    
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend
```

**封面裁剪提示**：微信在星标/常读用户侧展示 2.35:1 宽图，普通用户展示 1:1 方图。核心信息必须放在图片中央 1:1 区域内。

### 5.4 创建草稿

使用 `upload.py` 一键完成：头图上传注入 → 底部留白 → 封面上传 → 创建草稿。

```bash
python3 scripts/upload.py \
  --token ACCESS_TOKEN \
  --html output/article-inline.html \
  --title "文章标题（≤64字）" \
  --author "嗯哌" \
  --digest "摘要（≤120字）"
```

`upload.py` 内部流程：

**步骤 0**：去除 `<section>` 外层容器 → 让内容直接填满微信文章区宽度（v1.7.0）

**步骤 1**：上传 `img/header_image.png` → 获取微信 CDN URL → 注入 `<img>` 到正文最前面

**步骤 2**：追加底部留白 `<p style="margin:0;padding:0;height:0;"><br></p>` 到正文最后

**步骤 3**：上传 `img/cover.png` → 获取 `thumb_media_id`（若不存在则自动生成品牌色封面 fallback）

**步骤 4**：构建 payload → 🔴 铁律1 序列化 → 创建草稿

```python
# 🔴 关键：必须 ensure_ascii=False，否则中文变 \uXXXX → 微信编辑器显示乱码
# 🔴 必须用 data= 传 UTF-8 字节，不能用 json= 参数
payload_json = json.dumps(payload, ensure_ascii=False)
resp = requests.post(
    f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
    data=payload_json.encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8"},
    timeout=60,
)
```

关键约束：
- `title` ≤ 64 字，超长自动截断末尾加 `…`
- `content` 中的 HTML 已由 `upload.py` 自动注入头图和底部留白
- `thumb_media_id` 为**必填项**——`upload.py` 自动从 `img/cover.png` 获取

### 5.5 错误处理

| 错误码 | 含义 | 处理 |
|--------|------|------|
| 40001 | access_token 过期/无效 | 重新获取 token，重试 1 次 |
| 40007 | 不合法的媒体 ID | ① 检查 thumb_media_id 是否已正确上传；② 重新上传封面获取新 media_id；③ 确认上传时使用了 `type=image` 参数 |
| 40125 | 无效的 appsecret | 提示用户检查凭据，重新提供 |
| 45009 | 调用频率超限 | 等待 1 分钟后重试 |
| 50000+ | 微信服务器错误 | 等待 5 秒后重试，最多 3 次 |

### 5.6 成功响应

```json
{ "media_id": "xxx" }
```
保存 `media_id`，提示用户：**打开公众号后台 → 草稿箱 → 预览确认排版效果 → 群发**。

上传完成后，`upload.py` 自动清理临时文件，只保留 HTML 排版文件和原始 Markdown。

---

## 完整链路示例

### 示例 1：默认完整流程——优化 + 排版 + 发布

```
用户：帮我把这篇文章优化后发公众号
（附带 draft.md）

→ 阶段⓪：内容脱水 + 结构重组 + 去AI味
→ 🔴 输出优化稿 → 用户确认「可以」
→ 阶段①：analyze_content() → 推荐最佳排版系统
         preview_themes.py --open → 浏览器 6 套对比
         🔴 用户选择
         build_inline.py --theme <选定> → inline HTML
→ 阶段②：upload.py → 上传头图+封面 → 创建草稿
→ ✅ media_id 返回
```

### 示例 2：豁免优化 + 指定排版

```
用户：这篇按原文，用卡片流排版发公众号，一字不改

→ 豁免「一字不改」→ 跳过阶段⓪
→ 阶段①：用户指定「卡片流」→ build_inline.py --theme plum
→ 阶段②：upload.py → ✅
```

### 示例 3：自定义颜色

```
用户：主色用 #e63946，发公众号

→ 阶段⓪① 正常执行
→ 阶段①：build_inline.py --theme "#e63946" → 默认 classic 布局 + 自动推导配色
→ 阶段②：upload.py → ✅
```

---

## 与其它 Skill 的协作

- **oral-stylizer**：阶段⓪ 的前置处理器。口述碎碎念先调 oral-stylizer 结构化，再进入本 skill。
- **humanizer-zh**：阶段⓪.3 去 AI 味的执行引擎，直接调用审阅全文。

协作管线：`oral-stylizer → wechat-automator（⓪优化 → ①排版 → ②发布）`

### 配图扩展（预留口子）

本 skill 不内置配图生成。但 HTML 结构支持配图占位：

```html
<p class="illustration"><img src="PLACEHOLDER" alt="配图说明"></p>
```

配图准备完成后，替换 `PLACEHOLDER` 为微信 CDN URL 即可。`.illustration` 样式（居中、圆角、全宽）已在所有排版系统中内置。

未来可通过安装 `npie-illustrations` skill 实现自动配图流程（出 shot list → 生成 → 插入），两 skill 接口已预留对齐。

---

---

## 🔴 历史事故与铁律（2026-06-09 血泪教训）

以下每条都曾经导致过**批量乱码草稿**的生产事故。**违反任何一条 = 用户草稿箱被污染 = 不可接受。**

### 铁律 0：排版发布 = 必须调用本 skill

用户说「排版」「发布」「排版发布」「发公众号」「推送草稿」或任何含公众号发布意图的话 → **必须先用 `Skill` 工具加载 `wechat-automator`，然后严格按其五阶段流水线执行。** 严禁以下行为：

- ❌ 加载了 skill 但自己另写 Python 脚本绕过
- ❌ 手动拼接 HTML 直接用 `requests` 上传
- ❌ 用 `curl` 代替 skill 的 `build_and_upload.py`
- ❌ 跳过 class-based → html.parser → inline 转换管线

**skill 加载后的 `scripts/build_and_upload.py` 是唯一合法的执行入口。**

### 铁律 1：JSON 序列化必须 `ensure_ascii=False`

```python
# ❌ 错误：requests 的 json= 参数默认 ensure_ascii=True
# 中文 → \uXXXX → 微信编辑器不解码 → 草稿箱全乱码
resp = requests.post(url, json=payload)

# ✅ 正确：手动序列化，ensure_ascii=False
payload_json = json.dumps(payload, ensure_ascii=False)
resp = requests.post(url, data=payload_json.encode("utf-8"),
                     headers={"Content-Type": "application/json; charset=utf-8"})
```

**根因**：`requests.post(json=payload)` 内部调用 `json.dumps(payload)`，默认 `ensure_ascii=True`，所有非 ASCII 字符（中文）被转义为 `\uXXXX`。微信 API 虽接受请求并返回成功，但草稿编辑器**不解码**这些转义序列，直接显示为 `我把...`。

### 铁律 2：HTMLParser 必须 `convert_charrefs=False`

```python
# ❌ 错误：默认 convert_charrefs=True
# &lt;style&gt; → <style>（真标签）→ 微信/浏览器吃掉后续内容
parser = HTMLParser()  # 默认 convert_charrefs=True

# ✅ 正确
parser = HTMLParser(convert_charrefs=False)
# &lt;style&gt; 保持为实体引用 → handle_entityref('lt') → 正确输出 &lt;
```

**根因**：Python `HTMLParser` 默认 `convert_charrefs=True`，将 `&lt;` `&gt;` 等命名实体转为对应字符 `<` `>`。如果 `<code>&lt;style&gt;</code>` 被转为 `<code><style></code>`，`<style>` 被当作真标签，导致后面内容全部丢失。

### 铁律 3：只传 body 片段，不传完整 HTML 文档

```python
# ❌ 错误：传完整 HTML 文档给 content 字段
content = "<!DOCTYPE html><html><head>...</head><body>...</body></html>"

# ✅ 正确：只传 body 内部纯内容片段
# content = "<p>...</p><h2>...</h2><blockquote>...</blockquote>"
# 不含 <html>, <head>, <body>, <section> 外层包裹
```

**根因**：微信草稿 API 的 `content` 字段期望的是文章内文 HTML 片段，不是完整网页文档。传入 `<!DOCTYPE>` / `<html>` / `<head>` 标签会导致编辑器解析异常。

### 铁律 4：嵌套覆盖必须追踪父级 class

```python
# ❌ 错误：只追踪 tag 名，无法区分子元素的父容器类型
tag_stack = ["blockquote"]  # 丢失 class 信息
# golden-quote 下的 <p> 和 cta-footer 下的 <p> 都用了 blockquote p 样式

# ✅ 正确：追踪 (tag, class) 元组
tag_stack = [("blockquote", "golden-quote")]
# 先查 (class, tag) → (golden-quote, p) → 正确样式
# 再查 (tag, tag)   → (blockquote, p)    → 兜底样式
```

### 铁律 6：超长引用（>300 字）禁用 `<blockquote>`，改用 `<section>` + 左边框

```html
<!-- ❌ 错误：Prompt 全文等超长内容（>300字）包在 <blockquote> 中
     微信编辑器自动插入警告：「引用字数:1119/300(单次引用不得超过300字)」 -->
<blockquote>
  <p>你现在是我的Obsidian知识库资深架构师和重构专家...</p>
  <p>审查重点（必须覆盖）...</p>
  <!-- ...1100+ 字内容 -->
</blockquote>

<!-- ✅ 正确：用 <section> + border-left 替代，视觉等效但无字数警告 -->
<section style="border-left:3px solid #0d7377;margin:16px 0;padding:4px 0 4px 18px;">
  <p style="font-size:14px;color:#4a5a6a;">你现在是我的Obsidian知识库资深架构师和重构专家...</p>
  <p style="font-size:14px;color:#4a5a6a;">审查重点（必须覆盖）...</p>
</section>
```

**根因**：微信编辑器对 `<blockquote>` 元素有隐性 300 字上限检测。超过 300 字的单次引用会被自动插入警告文字，破坏排版。`<section>` 不受此限制，配合 `border-left` 样式可实现相同的视觉效果。

**适用范围**：Prompt 全文、长文摘录、多段落引用等任何可能超过 300 字的引用内容。短引用（≤300 字）仍可正常使用 `<blockquote>`。

### 铁律 5：上传前必须验证，验证必须排除 `<code>` 和 `<pre>`

```python
# ❌ 错误：全文搜索 <style，误判 <code>&lt;style&gt;</code> 中的内容
# ❌ 错误：全文搜索 <div，误判 <code>&lt;div&gt;</code> 中的内容

# ✅ 正确：先 strip <code> 和 <pre> 块，再验证其余部分
clean = re.sub(r'<code[^>]*>.*?</code>', '', html, flags=re.DOTALL)
clean = re.sub(r'<pre[^>]*>.*?</pre>', '', clean, flags=re.DOTALL)
# 然后在 clean 上做 <style>, <div>, class= 检查
```

### 铁律 7：微信不支持 `<pre>` 标签——所有换行全部丢失，内容变成一行（2026-06-26 实战血证）

```html
<!-- ❌ 致命错误：<pre> 在微信编辑器中被吃掉所有换行符
     CLAUDE.md 的 151 行内容变成一行，目录树结构完全塌缩 -->
<pre style="...">
# My‑Viki 系统规则
## 1. 角色与总目标
- 你是 **My‑Viki 的知识架构师和维护者**。
...
</pre>
<!-- 结果：微信草稿箱里变成一行乱码 -->
```

**根因**：微信编辑器不支持 `<pre>` 标签。`<pre>` 内的换行符（`\n`）被全部忽略，所有内容挤压成一行。同时 `<pre>` 的背景色和等宽字体样式也可能被剥离。

**✅ 唯一正确的替代方案：`<section>` + `white-space:pre-wrap` + 显式 `<br>` 换行**

```python
import html as html_mod

def text_to_wechat_block(content, style_extras=""):
    """
    将多行文本转为微信兼容的格式化区块。
    三步：① HTML 转义 → ② \n → <br> → ③ 包入 <section>
    """
    escaped = html_mod.escape(content)       # 转义 < > & "
    with_br = escaped.replace('\n', '<br>')  # 换行 → 显式 <br>
    return f'<section style="white-space:pre-wrap;font-family:monospace;{style_extras}">{with_br}</section>'
```

**关键样式说明**：
| 样式属性 | 作用 | 必要性 |
|----------|------|--------|
| `white-space:pre-wrap` | 保留空格缩进，配合 `<br>` 换行 | 🔴 必须 |
| `font-family:monospace` | 等宽字体，替代 `<pre>` 的默认等宽效果 | 🟡 强烈建议 |
| `max-height:520px;overflow-y:auto` | 长内容滚动（CLAUD.md/WIKI.md 等 150+ 行文件） | 🟡 按需 |
| `-webkit-overflow-scrolling:touch` | iOS 平滑滚动 | 🟡 按需 |

**适用范围**：目录树、代码块、配置文件全文、Markdown 原文展示——任何依赖换行和空格对齐的格式化文本，一律用此方案，**禁止使用 `<pre>`**。

**禁止 `<pre>` 的唯一例外**：`build_inline.py` 的验证逻辑中，`<pre>` 仅在 `<code>` 展示 HTML 标签转义示例（如 `&lt;style&gt;`）时可用于 class-based 中间文件，但**最终输出到微信的 HTML 必须零 `<pre>`**。

---

## 安全与隐私

- API 凭据（AppID / AppSecret）优先级：环境变量 → 会话上下文 → 主动询问。仅在当前会话内存缓存，不写入任何磁盘文件
- 生成的 HTML 和草稿内容保存在本地，不经过第三方服务中转
- 上传完成后自动清理临时文件（JSON payload、自动生成的封面 PNG）
- 凭据在日志和输出中不出现明文
