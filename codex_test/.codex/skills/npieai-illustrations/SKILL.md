---
name: NpieAI-illustrations
description: 生成 嗯哌AI (NpieAI) 风格的中文方法论大纲逻辑图/逻辑大图。适用于将视频脚本或文章整体大纲提炼为一张或多张包含“大标题、副标题、多个带编号和标题的小模块、连接箭头、核心逻辑链条”的完整手绘大图。必须使用手写粗体大标题与副标题、带圈数字编号小框、彩铅温暖填充与纯白底色。绝不包含“嗯哌”名字字标。
version: 1.1.0
author: 嗯哌AI(NpieAI)
---

# 🎨 嗯哌AI (NpieAI) 手绘大纲逻辑信息图生成规范

本技能用于将视频脚本、文章大纲或方法论框架，提炼并生成为一系列逻辑清晰、视觉温暖的手绘大纲逻辑图，专为录屏讲解及完整视频大纲展示设计。

---

## ⚔️ 与 npie-illustrations 技能的分工与防冲突

为防止大模型在唤醒时产生冲突，两款技能做如下严格分工：
*   **npie-illustrations（文章正文配图）**：用于生成**单幅概念插画**、**正文片段配图**。特点是没有图片大标题、没有大段流程框架，只表达单个隐喻、段落观点或人物状态。
*   **NpieAI-illustrations（大纲方法论逻辑图 - 本技能）**：用于生成**整幅大纲图、方法论框架图、多步骤流程大图**。特点是带手绘大标题、副标题、步骤编号框、箭头逻辑线，且用于视频讲解。

---

## 🎨 视觉风格与结构 DNA

### 1. 顶部标题区域 (Header)
*   **大标题**：顶部中央或偏左，粗体中文手写字，字形温暖、圆润，带有手工描边感。
*   **副标题**：大标题下方，较小字号的手写字，用于解释核心理念。
*   **文字字体（硬性要求）**：图上所有中文大标题、副标题、步骤框标题与说明词，**必须且只能使用手绘美术字（strictly handwritten style Chinese calligraphy only）**，严禁使用任何标准的黑体、宋体、微软雅黑等数字印刷字体。

### 2. 核心视觉 IP 形象 (Visual IP)
画面使用以下视觉 IP：
*   **卡通 IP 主角（“嗯哌”）**：一个可爱的手绘女生，黑色/深褐色长发（中分，无刘海），身穿**白色针织粗线毛衣**与浅色裤子。眼神温暖，面部圆润。
*   **“AI机器人助手”**：可爱的纯白小机器人，头部圆润，**头顶有两根可爱的天线**，面部是带有豆豆眼的矩形屏幕。
*   **绝对限制**：**绝对禁止在图片上打出“嗯哌”或“嗯哌哌”这几个汉字作为文本标签**。IP 形象自然融入画面动作即可，不需做名字标注。

### 3. IP 形象参考图路径 (IP References)
生成图片时，必须将以下本机路径的图片作为 `ImagePaths`（最多3张）传给生图工具以保持一致性：
*   **女主角半身头像参考**：`./assets/ip-references/cartoon_ip_character_v2.png`
*   **女主角全身及白毛衣参考**：`./assets/ip-references/cartoon_ip_fullbody_clean_v1.png`
*   **动作姿势库**：
    *   挥手：`./assets/ip-references/cartoon_ip_v2_fullbody_wave.png`
    *   坐姿：`./assets/ip-references/cartoon_ip_v2_fullbody_sit.png`
    *   开心/比耶：`./assets/ip-references/cartoon_ip_v2_fullbody_peace.png`

### 4. 逻辑模块网格 (Grid & Steps)
*   **模块小框**：每个逻辑步骤必须包含在一个黑色手写圆角框线中。
*   **步骤标题**：左上角带圈数字编号（`①`, `②` 等），以及加粗的小步骤手写标题与说明。
*   **逻辑连线**：步骤框之间由橙色或黑色手绘弯曲箭头指示流程。
*   **中央转换公式**：在画面过渡区域设计手绘转换关系框（如 `流量数据 ➔ 视频脚本`）。

### 5. 色彩与留白 (Color & Whitespace)
*   **底色**：干净的纯白背景。尺寸根据用户指定的比例（如 16:9 横屏，或 3:4, 9:16 竖屏）生成。
*   **配色**：深灰线条 + 彩铅/轻水彩淡雅填色。暖粉用于主角肤色，橙色/黑色引导线，少量红色用于关键提醒。

---

## 📝 绘图提示词模板 (Prompt Template)

生成大纲逻辑图时，必须使用如下英文提示词框架，并将引用的参考图文件名传给 `ImagePaths`：

```text
Generate one standalone {尺寸比例} Chinese methodology infographic mapping an entire workflow logic.

Visual Style:
Pure white background, clean and minimalist. Warm hand-drawn sketch style with soft pencil/ink lines and colored-pencil/light watercolor textures. Sparse, cozy hand-drawn details. High contrast but soft coloring. No complex shadows, no paper textures, no vector illustrations, no PPT slide structures.

Typography & Title:
At the top, a prominent handwritten bold Chinese title: "{大标题}" with a cute hand-drawn spark next to it. Below it, a smaller handwritten Chinese subtitle: "{副标题}". 
CRITICAL TYPOGRAPHY RULE: ALL Chinese text, titles, subtitles, and labels on the image MUST be strictly rendered in a cute, rounded, bold handwritten font (handwritten Chinese calligraphy style). Absolutely NO clean digital computer font rendering (such as HeiTi, SongTi, Arial). The font must look 100% manually drawn.

Layout & Logic Flow:
A structured diagram showing {数量} rounded hand-drawn boxes connected by curving orange flow arrows to represent a clear loop or progression.
In the center or transition area, show a small connection box: "{核心转换概念/公式}".

Box 1: "{步骤1标题}"
- Marked with a colored badge circled number "1".
- Subtitle: "{步骤1副标题}".
- Inside sketch: {步骤1手绘画面描述}.

Box 2: "{步骤2标题}"
- Marked with a colored badge circled number "2".
- Subtitle: "{步骤2副标题}".
- Inside sketch: {步骤2手绘画面描述}.

Box 3: "{步骤3标题}"
- Marked with a colored badge circled number "3".
- Subtitle: "{步骤3副标题}".
- Inside sketch: {步骤3手绘画面描述}.

Box 4: "{步骤4标题}"
- Marked with a colored badge circled number "4".
- Subtitle: "{步骤4副标题}".
- Inside sketch: {步骤4手绘画面描述}.

Characters & IP:
Draw the characters matching the reference images. 
1. The main character is a cute girl with long dark hair, wearing a white knit sweater and light pants, behaving friendly and smiling. 
2. A cute simple white helper robot representing AI assistance, with a rounded head and two antennas.
CRITICAL: Do NOT write any name label such as "嗯哌" or "嗯哌哌" next to the character.

Color Palette:
Dark gray outlines. Soft pink/peach for skin and character warmth. Pastel blue, yellow, and green tints inside step badges/boxes. Curving flow arrows in light hand-drawn orange. Sparse red markings for key emphasis.

Constraints:
Ensure the layout is spacious and readable. All Chinese titles and annotations must be beautifully handwritten. The entire structure must feel logically clear, structured, and easy to follow at a glance. Do not print any raw English tags like Box 1 or Box 2. All text shown on the image must be in Chinese except technical terms.
```

---

## 🛠️ 脚本大纲分析与大图策划工作流

当你接收到用户的视频脚本或大纲时，必须执行以下步骤：

### 1. 深度研读与全量大纲剖析 (Deep Analysis)
为了保证录屏讲解的完整性，**绝对不允许漏掉任何关键的方法论内容**。你必须：
*   详尽阅读脚本的每一段，理清全部核心逻辑节点。
*   规划的图片数量必须完整覆盖以下三个核心面：**【开场钩子/核心痛点】、【实操使用核心流程/步骤方法】、【产出交付与结尾升华】**。
*   根据脚本的篇幅与内容厚度，智能判断并设计最合理的**推荐生成张数**。每一张推荐的逻辑图，都必须具体指出其承接了脚本的哪几行内容，确保讲解过程不留盲区。

### 2. 输出策划方案（向用户确认）
向用户提供剖析结果，包括：
*   **推荐生成的总张数及策划理由**。
*   **每张图的详细设计清单**（大标题、副标题、逻辑块划分、中心转换公式）。
*   **明确提问**：
    1.  **您期望本次生成几张信息图？**（用户可调整推荐值）
    2.  **您需要什么尺寸比例？**

### 3. 等待用户指令
在得到用户关于“数量”和“尺寸”的明确确认前，**绝对不能**调用生图工具。

### 4. 生成与交付
用户确认后，调用生图工具按用户要求的尺寸生成，并保存交付。
