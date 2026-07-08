---
name: excalidraw-visualizer
version: 1.0.1
description: "将文章内容可视化为 Excalidraw 手绘图表的 skill。当用户提供文章（粘贴文字 / .md / .docx / .txt / .pdf 文件路径）并希望将其内容画成信息卡片、对比表格、流程图、闭环图、树形图、时间线或思维导图时触发。也适用于用户希望给文章配上手绘风格配图、插图、示意图的可视化场景。"
---

# Excalidraw Visualizer Skill

将文章内容自动转化为 Excalidraw 手绘图表。
支持 7 种图表类型（含 visual_card）+ 5 种风格预设。

**核心参考文件：**
- `references/diagram-templates.md` — 结构化数据 schema
- `references/visualization-analysis-guide.md` — LLM 深度分析框架
- `references/style-presets.json` — 风格预设（professional/warm/minimal/vivid/dark）

---

## 工作流

### Step 1: 接收输入

判断用户输入类型：

| 输入形式 | 处理方式 |
|---------|---------|
| 直接粘贴的文字 | 直接作为 raw_text |
| 文件路径 (.md / .txt) | 直接读取 |
| 文件路径 (.docx) | `python3 scripts/extract.py "<path>"` → raw_text |
| 文件路径 (.pdf) | `python3 scripts/extract.py "<path>"` → raw_text |

**如果文件路径不存在，直接报错，不要尝试自己猜路径。**

### Step 2: LLM 深度分析

通读全部文本，遵循 `references/visualization-analysis-guide.md` 的分段分析方法：

1. **逐段扫描**，识别 7 种结构模式（flowchart/comparison/tree/timeline/mindmap/cycle/visual_card）
2. **匹配图表类型**，填充对应的 structured data JSON schema
3. **检查** 节点数量、文本长度、ID 一致性（详见分析指南 5. 质量控制）
4. **多个图表**按文章内容出现顺序排列到 diagrams 数组
5. **从 `references/style-presets.json` 选择一个风格**，输出 `"style": "professional"`（或其他）

**输出格式示例：**

```json
{
  "style": "professional",
  "diagrams": [
    {
      "type": "flowchart",
      "title": "用户注册流程",
      "nodes": [
        {"id": "n1", "label": "开始", "shape": "rounded"},
        {"id": "n2", "label": "填写信息", "shape": "rect"},
        {"id": "n3", "label": "信息合规？", "shape": "diamond"},
        {"id": "n4", "label": "注册成功", "shape": "rounded"}
      ],
      "edges": [
        {"from": "n1", "to": "n2", "label": ""},
        {"from": "n2", "to": "n3", "label": ""},
        {"from": "n3", "to": "n4", "label": "是"},
        {"from": "n3", "to": "n2", "label": "否"}
      ]
    }
  ]
}
```

### Step 3: 调用 layout.py

将生成的 structured data JSON 写入临时文件，然后执行：

```bash
python3 .claude/skills/excalidraw-visualizer/scripts/layout.py \
  --input /tmp/excalidraw_input.json \
  --output "<输出文件路径>.excalidraw"
```

layout.py 会自动根据 `style` 字段加载对应的风格预设。

**输出文件路径规则：**
- 如果输入是文件路径：输出到输入文件同目录，文件名 = 输入文件名 + `_visualized.excalidraw`
- 如果输入是粘贴文字：输出到当前工作目录，文件名 = `article_visualized.excalidraw`

### Step 4: 告知用户

- 告知用户文件已生成
- 提示用户将文件拖入 Excalidraw（默认 `http://localhost:3000`）
- 列出每个图表的标题和类型

### Step 5: 迭代修改

如果用户不满意，支持迭代：

- "第二个流程图再加一个节点" → 修改对应 structured data → 重新调用 layout.py
- "换个配色" → 修改 `style` 字段 → 重新调用 layout.py
- "再加一个时间线图" → 在 diagrams 数组追加 → 重新调用 layout.py
- "删除第三个图" → 从 diagrams 数组删除 → 重新调用 layout.py

---

## 设计风格

所有图表使用 **Excalidraw 手绘风格**：
- `roughness: 2` — 强烈手绘感（或根据预设变化）
- `fontFamily: 1` — Virgil 手写字体
- 风格预设通过 `style` 字段选择，详见 `references/style-presets.json`

## 图标库

300+ 预置图标，从 18 个 Excalidraw 公开库自动下载提取。图标通过 `decorations` 字段放置：

```json
"decorations": [
  {"type": "icon", "name": "StickMan", "position": "top-right", "scale": 0.6}
]
```

**命名规则：`{库名}_{图标名}`**，例如 `Icons_search`、`Network_Server`。

| 分类 | 示例图标名 | 数量 |
|------|-----------|------|
| **Stick Figures** | StickMan, Girl, Guy, Happy, Sad, Child, Shrug | 9 |
| **Icons** (文件/编程) | Icons_search, Icons_cloud, Icons_download, Icons_upload, Icons_share, Icons_message, Icons_code, Icons_pdf, Icons_zip | 65 |
| **Network** | Network_Server, Network_Router, Network_Firewall, Network_VPN, Network_Switch, Network_Hub | 10 |
| **Gadgets** | Device, Smartphone, Tablet, Laptop, MP3Player, Smartwatch | 5 |
| **Computers** | Computers_item_0~3 (台式/服务器/显示器) | 4 |
| **IT Logos** | IT Logos_Docker, IT Logos_React, IT Logos_Python, IT Logos_Kubernetes, IT Logos_Kafka | 30 |
| **Cloud Apps** | Cloud Apps_Facebook, Cloud Apps_TikTok, Cloud Apps_Instagram, Cloud Apps_WordPress | 15 |
| **Emojis** | Emojis_item_0~47 (48个表情符号) | 48 |
| **Bubbles** | Bubbles_item_0~3 (2个对话泡+2个思想泡) | 4 |
| **Hearts** | Hearts_item_0~4 (多种心形) | 5 |
| **Charts** | Charts_item_0~3 (柱状/折线/饼图) | 4 |
| **System Icons** | System Icons_bar_graph, System Icons_line_graph, System Icons_lightning, System Icons_star, System Icons_warn | 24 |
| **Clocks** | Clocks_Alarm_clock, Clocks_Wall_clock, Clocks_Wristwatch | 3 |
| **Maps** | Maps_item_0~3 (地图+定位针) | 4 |
| **GitHub Icons** | GitHub Icons_item_0~6 (branch/commit/merge/PR) | 7 |
| **Storytelling** | Storytelling_item_0~15 (情绪人物/动作/物件) | 14 |
| **Software Arch** | Software Architecture_item_0~6 (微服务/数据库/缓存) | 7 |
| **Awesome Icons** | Awesome Icons_item_0~23 (通用图标) | 24 |

如需扩展，运行 `python3 scripts/download_icons.py` 即可从所有公开库重新下载。

---

## 依赖

```bash
pip install python-docx markitdown
```

如果用户没有安装，提醒他们安装。
