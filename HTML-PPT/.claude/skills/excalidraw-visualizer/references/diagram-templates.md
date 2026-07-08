# 图表类型模板

定义 LLM → layout.py 中间数据格式。
LLM 分析文章后，按此 schema 输出结构化数据。

---

## flowchart (流程图)

适用场景：流程步骤、决策分支、业务逻辑、操作指南

```json
{
  "type": "flowchart",
  "title": "用户注册流程",
  "nodes": [
    {"id": "n1", "label": "开始", "shape": "rounded"},
    {"id": "n2", "label": "填写注册信息", "shape": "rect"},
    {"id": "n3", "label": "信息合规？", "shape": "diamond"},
    {"id": "n4", "label": "发送验证码", "shape": "rect"},
    {"id": "n5", "label": "验证通过？", "shape": "diamond"},
    {"id": "n6", "label": "注册成功", "shape": "rounded"}
  ],
  "edges": [
    {"from": "n1", "to": "n2", "label": ""},
    {"from": "n2", "to": "n3", "label": ""},
    {"from": "n3", "to": "n4", "label": "是"},
    {"from": "n3", "to": "n2", "label": "否"},
    {"from": "n4", "to": "n5", "label": ""},
    {"from": "n5", "to": "n6", "label": "通过"},
    {"from": "n5", "to": "n4", "label": "不通过"}
  ]
}
```

**节点 shape 取值**: `rect` (矩形) | `diamond` (菱形) | `rounded` (圆角矩形) | `ellipse` (椭圆)

---

## comparison (对比图)

适用场景：方案对比、优缺点、前后差异、参数对比

```json
{
  "type": "comparison",
  "title": "方案对比",
  "left_header": "方案A",
  "right_header": "方案B",
  "items": [
    {"feature": "开发成本", "left": "高", "right": "低"},
    {"feature": "运行效率", "left": "90%", "right": "70%"},
    {"feature": "可维护性", "left": "优秀", "right": "一般"},
    {"feature": "扩展能力", "left": "强", "right": "中等"}
  ]
}
```

items 数量任意，layout.py 自动分配行高。

---

## tree (树形结构)

适用场景：组织架构、分类体系、目录结构、层级关系

```json
{
  "type": "tree",
  "title": "公司组织架构",
  "root": {
    "id": "r",
    "label": "CEO",
    "children": [
      {
        "id": "c1", "label": "CTO",
        "children": [
          {"id": "c1a", "label": "前端团队", "children": []},
          {"id": "c1b", "label": "后端团队", "children": []},
          {"id": "c1c", "label": "运维团队", "children": []}
        ]
      },
      {
        "id": "c2", "label": "CFO",
        "children": [
          {"id": "c2a", "label": "财务部", "children": []}
        ]
      },
      {
        "id": "c3", "label": "COO",
        "children": [
          {"id": "c3a", "label": "运营部", "children": []},
          {"id": "c3b", "label": "市场部", "children": []}
        ]
      }
    ]
  }
}
```

嵌套深度无限制，但建议不超过 4 层。

---

## timeline (时间线)

适用场景：发展历程、项目排期、历史事件、路线图

```json
{
  "type": "timeline",
  "title": "公司发展历程",
  "events": [
    {
      "id": "e1",
      "date": "2024 Q1",
      "title": "公司成立",
      "description": "完成 500 万天使轮融资"
    },
    {
      "id": "e2",
      "date": "2024 Q3",
      "title": "产品 1.0 发布",
      "description": "首个公开版本上线，获得 1000 注册用户"
    },
    {
      "id": "e3",
      "date": "2025 Q1",
      "title": "A 轮融资",
      "description": "完成 3000 万 A 轮融资"
    },
    {
      "id": "e4",
      "date": "2025 Q3",
      "title": "用户破百万",
      "description": "累计注册用户突破 100 万"
    }
  ]
}
```

events 按时间顺序排列，layout.py 等距分布在轴线上。

---

## mindmap (思维导图)

适用场景：知识梳理、头脑风暴、概念分解、学习笔记

```json
{
  "type": "mindmap",
  "title": "AI 知识体系",
  "root": {
    "id": "r",
    "label": "人工智能",
    "branches": [
      {
        "id": "b1",
        "label": "机器学习",
        "branches": [
          {"id": "b1a", "label": "监督学习", "branches": []},
          {"id": "b1b", "label": "无监督学习", "branches": []},
          {"id": "b1c", "label": "强化学习", "branches": []}
        ]
      },
      {
        "id": "b2",
        "label": "深度学习",
        "branches": [
          {"id": "b2a", "label": "CNN", "branches": []},
          {"id": "b2b", "label": "RNN", "branches": []},
          {"id": "b2c", "label": "Transformer", "branches": []}
        ]
      },
      {
        "id": "b3",
        "label": "NLP",
        "branches": []
      }
    ]
  }
}
```

用 `branches` 替换 `children`，layout.py 使用左→右树形布局（区别于 tree 的上→下）。

---

## cycle (循环/回路)

适用场景：循环流程、反馈回路、反复迭代的步骤

```json
{
  "type": "cycle",
  "title": "Loop 最小环节",
  "nodes": [
    {"id": "n1", "label": "执行", "icon": "⚙️", "shape": "rounded"},
    {"id": "n2", "label": "检查", "icon": "🔍", "shape": "rect"},
    {"id": "n3", "label": "纠错", "icon": "🔧", "shape": "rect"},
    {"id": "n4", "label": "记录状态", "icon": "📝", "shape": "rect"}
  ],
  "edges": [
    {"from": "n1", "to": "n2", "label": ""},
    {"from": "n2", "to": "n3", "label": ""},
    {"from": "n3", "to": "n4", "label": ""}
  ],
  "exit_node": {
    "id": "d1",
    "label": "达标？",
    "icon": "✅",
    "shape": "diamond",
    "on_yes": {"id": "e1", "label": "输出结果", "icon": "🎯"},
    "on_no_label": "不达标"
  }
}
```

**布局规则**:
- 循环节点水平排成一排（从左到右）
- 每个节点可设置 `icon` 显示在标签前
- 退出节点（菱形）居中放在循环节点下方
- "是" 分支向右到输出节点
- "否" 路径从退出节点底部→向下→向左→向上回到第一个循环节点形成闭环
- 回流路径走底部通道，不交叉任何元素

---

## visual_card (视觉卡片)

适用场景：核心段落美化、引言高亮、关键观点呈现

卡片支持多种 `card_style` 变体，丰富视觉节奏：

**rounded** (默认)
标准圆角卡片，柔和填充色，适合通用内容呈现。

**accent-left**  
左侧彩色强调条 + 圆角卡片，适合"痛点""结论"等需要视觉锚点的内容。

**accent-top**  
顶部彩色强调条，适合分段标题类的卡片。

**pattern**  
交叉斜线 (cross-hatch) 填充纹理，用于突出"原理""机制"等需要视觉区隔的内容。

**minimal**  
透明背景 + 细边框，适合补充说明、备注类轻量内容。

**banner**  
加宽版 + 更大标题字号 + 宽松行距，适合"总结""金句"等需要强视觉收尾的内容。

```json
{
  "type": "visual_card",
  "title": "核心观点",
  "icon": "💡",
  "card_style": "accent-left",
  "content": "选择大于努力。\n在 AI 时代，真正稀缺的不是技术能力，\n而是定义问题的能力。",
  "decorations": [
    {"type": "icon", "name": "User", "position": "top-right", "scale": 0.6}
  ]
}
```

卡片会自动适配内容高度。decoration icon 从 `decorations` 字段指定，图标从 icons.json 取（User/Users/Device/Server/Email/Docker/Slack/GitHub 等）。

---

## decorations (装饰字段)

任何图表类型都可以附加 `decorations` 数组，在合适的位置贴图标：

```json
{
  "type": "flowchart",
  "title": "系统架构",
  "nodes": [...],
  "edges": [...],
  "decorations": [
    {"type": "icon", "name": "Server", "position": "top-right", "scale": 0.5},
    {"type": "icon", "name": "User", "position": "inline-left", "scale": 0.5}
  ]
}
```

**position 取值**: `top-right` | `top-left` | `bottom-right` | `inline-left` | `top-center`

---

## 多图输出

一篇文章可能包含多个适合可视化的段落，
LLM 应输出数组 `diagrams`，每个元素是一种图表：

```json
{
  "diagrams": [
    { "type": "flowchart", "title": "...", "nodes": [...], "edges": [...] },
    { "type": "comparison", "title": "...", ... },
    { "type": "tree", "title": "...", ... }
  ]
}
```

所有图表将纵向排列在同一个 `.excalidraw` 画布中。

---

## sketchnote (手绘信息图)

适用场景：手绘风格步骤图、卡通信息图、教程/工作坊风格的带图标的步骤说明

```json
{
  "type": "sketchnote",
  "title": "用 AI 工具也能赚钱？",
  "subtitle": "零基础搞定自动化工作流的四个步骤",
  "steps": [
    {
      "id": "s1",
      "title": "找到重复任务",
      "subtitle": "日常工作中的枯燥环节",
      "icon": "User",
      "color": "yellow"
    },
    {
      "id": "s2",
      "title": "配置 AI 流程",
      "subtitle": "Zapier + Claude 连接",
      "icon": "Cloud Apps_Zapier",
      "color": "blue"
    },
    {
      "id": "s3",
      "title": "测试与学习",
      "subtitle": "观察 AI 如何理解你",
      "icon": "System Icons_magic_wand",
      "color": "pink"
    },
    {
      "id": "s4",
      "title": "放大收益",
      "subtitle": "从节省时间到创造价值",
      "icon": "Icons_share",
      "color": "green"
    }
  ]
}
```

**布局规则**:
- 大标题居中 + 副标题 + 星星/火花涂鸦装饰
- 每个步骤一张彩色卡片，左侧图标 + 标题 + 副标题
- 步骤之间竖向箭头连接
- `color` 取值: yellow / blue / pink / green / purple / orange

---

## LLM 图表类型选择策略

| 文章内容特征 | 推荐图表类型 |
|-------------|-------------|
| 循环、反馈回路、反复迭代 | cycle |
| 步骤、流程、决策、因果关系 | flowchart |
| 手绘风格信息图、教程步骤、带图标的流程图 | sketchnote |
| 对比、差异、优劣、参数对照 | comparison |
| 层级、分类、组织、嵌套关系 | tree |
| 时间顺序、发展历程、阶段 | timeline |
| 概念关联、知识拆解、发散思维 | mindmap |
| 核心段落、引言、痛点、金句 | visual_card (accent-left / banner) |
| 机制、原理、技术细节 | visual_card (pattern) |
| 补充说明、备注 | visual_card (minimal) |
