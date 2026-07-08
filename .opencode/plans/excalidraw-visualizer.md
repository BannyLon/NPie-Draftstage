# Excalidraw Visualizer Skill — Implementation Plan

## 目录结构

```
.claude/skills/excalidraw-visualizer/
├── SKILL.md
├── scripts/
│   ├── extract.py      # 多格式文本提取 (.md/.txt/.docx/.pdf)
│   ├── layout.py       # 布局引擎 → Excalidraw JSON (核心, ~500行)
│   └── open.py         # 自动打开接口 (骨架预留)
├── references/
│   ├── excalidraw-schema.md   # Excalidraw 元素模型 schema
│   └── diagram-templates.md   # 5种图表类型的结构化数据定义
└── LICENSE
```

---

## 文件 1: scripts/extract.py

```python
#!/usr/bin/env python3
"""Extract plain text from .md / .txt / .docx / .pdf"""

import sys, os, argparse

def extract_from_markdown(path):
    with open(path) as f:
        return f.read()

def extract_from_text(path):
    with open(path) as f:
        return f.read()

def extract_from_docx(path):
    import docx
    doc = docx.Document(path)
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paras)

def extract_from_pdf(path):
    import markitdown
    return markitdown.MarkItDown().convert(path).text_content

EXTRACTORS = {'.md': extract_from_markdown, '.txt': extract_from_text,
              '.docx': extract_from_docx, '.pdf': extract_from_pdf}

def extract(path):
    _, ext = os.path.splitext(path)
    fn = EXTRACTORS.get(ext.lower())
    if not fn:
        raise ValueError(f"Unsupported: {ext}")
    return fn(path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("filepath")
    print(extract(p.parse_args().filepath))
```

---

## 文件 2: scripts/layout.py

完整布局引擎，支持 5 种图表类型。架构如下：

```
ExcalidrawBuilder
├── _layout_flowchart()     # BFS 分层布局
├── _layout_comparison()    # 双栏网格布局
├── _layout_tree()          # 递归树形布局
├── _layout_timeline()      # 水平轴线布局
└── _layout_mindmap()       # 左→右树形布局
```

**关键设计决策：**
- LLM 输出 structured data（节点/关系），layout.py 计算像素坐标
- 手绘风格参数：roughness=2, fontFamily=1(Virgil), 软色填充
- 中文文本宽度估算：CJK字符×fontSize + ASCII×fontSize×0.55
- 多种图表在画布中纵向堆叠，间隔 80px
- 每个元素生成随机 seed，Excalidraw 渲染出不同手绘抖动

### 各布局算法

#### Flowchart (流程图)
```
1. 根据 edges 构建邻接表
2. BFS 从根节点分层（拓扑排序）
3. 同层 Y 相同，层内水平均匀分布
4. 箭头从源节点底部 → 目标节点顶部
5. 节点形状: process=rect, decision=diamond, start/end=rounded
```

#### Comparison (对比图)
```
1. 标题居中
2. 左右两列 + 中间竖线分隔
3. 交替行背景色
4. 特征名在列左侧对齐
```

#### Tree (树形结构)
```
1. 递归计算子树宽度
2. 父节点居中于子节点上方
3. 从父节点底部 → 子节点顶部的连线
4. 适用于: 组织架构、分类体系、目录结构
```

#### Timeline (时间线)
```
1. 水平轴线贯穿画布
2. 事件等距分布在轴线上
3. 事件标记（圆形）+ 上方日期 + 下方标题/描述
4. 适用于: 发展历程、项目计划、历史事件
```

#### Mindmap (思维导图)
```
1. 中心主题在左侧
2. 一级分支向右展开
3. 二级分支继续向右
4. 左→右树形布局（Tree 的变体）
5. 适用于: 知识梳理、头脑风暴、概念分解
```

### Excalidraw JSON 生成细节

- 形状类型映射: rect→rectangle, diamond→diamond, rounded→rectangle+roundness
- 文本与容器绑定: 形状的 boundElements 引用文本ID, 文本的 containerId 引用形状ID
- 箭头绑定: startBinding/endBinding 引用连接的元素
- 手绘: roughness=2, seed=随机, strokeWidth=2

### 配色方案 (手绘风格软色)

| 元素 | 填充色 | 用途 |
|------|--------|------|
| Process | #e7f5ff (淡蓝) | 流程节点 |
| Decision | #fff3bf (淡黄) | 决策节点 |
| Terminal | #d3f9d8 (淡绿) | 开始/结束 |
| Comparison Left | #e7f5ff (淡蓝) | 对比左列 |
| Comparison Right | #fff0f6 (淡粉) | 对比右列 |
| Tree | #f3f0ff (淡紫) | 树节点 |
| Arrow | #495057 (灰) | 连线 |
| Stroke | #1e1e1e (深灰) | 所有描边 |

---

## 文件 3: scripts/open.py

```python
"""自动打开 Excalidraw 文件（骨架，二期实现）"""

import os, webbrowser

EXCALIDRAW_URL = os.environ.get("EXCALIDRAW_URL", "http://localhost:3000")

def open_in_excalidraw(filepath):
    """
    自动在浏览器中打开 .excalidraw 文件。
    当前为骨架实现，仅打印提示。
    
    二期实现选项：
    A: 通过 Excalidraw URL hash 参数 (`#json=...`)
    B: 文件监听 + WebSocket 推送刷新
    C: Excalidraw Electron 桌面 App IPC
    """
    print(f"[open.py] 自动打开功能将在二期实现")
    print(f"[open.py] 请手动将文件拖入 Excalidraw ({EXCALIDRAW_URL})")
    print(f"[open.py] 文件路径: {filepath}")

if __name__ == "__main__":
    import sys
    open_in_excalidraw(sys.argv[1])
```

---

## 文件 4: references/excalidraw-schema.md

```markdown
# Excalidraw 元素格式参考

## .excalidraw 文件结构

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "excalidraw-visualizer-skill",
  "elements": [...],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

## 元素类型

| type | 说明 | 特有属性 |
|------|------|----------|
| rectangle | 矩形 | roundness |
| diamond | 菱形 | - |
| ellipse | 椭圆 | - |
| arrow | 箭头 | points, startBinding, endBinding, endArrowhead |
| text | 文本 | text, fontSize, fontFamily, textAlign, containerId |
| line | 直线 | points |

## 关键属性

- **roughness**: 0=完美, 1=轻微手绘, 2=强烈手绘
- **seed**: 随机种子，不同值产生不同手绘抖动效果
- **fontFamily**: 1=Virgil(手写体), 2=Normal, 3=Code
- **roundness.type**: 2=小圆角, 3=全圆角(pill)
- **boundElements**: 形状上绑定的元素（如文本）
- **containerId**: 文本所在的容器形状ID
- **points**: 箭头/线段的路径点 [[x1,y1], [x2,y2], ...]
```

---

## 文件 5: references/diagram-templates.md

```markdown
# 图表类型模板

定义 LLM→layout.py 中间数据格式。

## flowchart
```json
{
  "type": "flowchart",
  "title": "注册流程",
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
```

## comparison
```json
{
  "type": "comparison",
  "title": "方案对比",
  "left_header": "方案A",
  "right_header": "方案B",
  "items": [
    {"feature": "成本", "left": "低", "right": "高"},
    {"feature": "效率", "left": "90%", "right": "70%"}
  ]
}
```

## tree
```json
{
  "type": "tree",
  "title": "组织架构",
  "root": {
    "id": "r", "label": "CEO",
    "children": [
      {"id": "c1", "label": "CTO", "children": [{"id": "c1a", "label": "前端"}, {"id": "c1b", "label": "后端"}]},
      {"id": "c2", "label": "CFO", "children": []}
    ]
  }
}
```

## timeline
```json
{
  "type": "timeline",
  "title": "发展历程",
  "events": [
    {"id": "e1", "date": "2024 Q1", "title": "公司成立", "description": "完成首轮融资"},
    {"id": "e2", "date": "2024 Q3", "title": "产品发布", "description": "首个版本上线"}
  ]
}
```

## mindmap
```json
{
  "type": "mindmap",
  "title": "AI 知识体系",
  "root": {
    "id": "r", "label": "人工智能",
    "branches": [
      {"id": "b1", "label": "机器学习",
       "branches": [{"id": "b1a", "label": "监督学习"}, {"id": "b1b", "label": "无监督学习"}]},
      {"id": "b2", "label": "深度学习",
       "branches": []}
    ]
  }
}
```

## 选择策略

LLM 根据文章内容选择类型：
- **流程/步骤/决策** → flowchart
- **对比/优劣/差异** → comparison
- **层级/分类/组织** → tree
- **时间顺序/发展** → timeline
- **知识梳理/概念关联** → mindmap
- **混合** → 对每个段落分别判断，产出多个 diagram
```

---

## 文件 6: SKILL.md 核心逻辑

```markdown
---
name: excalidraw-visualizer
description: "将文章内容可视化为 Excalidraw 图表。当用户提供文章(粘贴/文件路径)并希望将其内容画成流程图、对比图、树形结构、时间线或思维导图时触发。"
---

## 工作流

### Step 1: 接收输入
- 纯文本: 直接使用
- 文件路径: `python scripts/extract.py <path>` → raw_text

### Step 2: LLM 深度分析
通读全文，识别可视觉化的段落，对每个段落：
1. 判断最适合的图表类型
2. 提取关键信息
3. 填充 structured data（格式见 references/diagram-templates.md）

输出示例：
```json
{
  "diagrams": [
    { "type": "flowchart", "title": "...", "nodes": [...], "edges": [...] },
    { "type": "comparison", "title": "..." , "items": [...] }
  ]
}
```

### Step 3: 调用 layout.py
将 structured data 写入临时文件，执行：
```bash
python scripts/layout.py --input /tmp/struct.json --output <文件名>.excalidraw
```

### Step 4: 输出
- 文件生成到输入文件所在目录（或当前目录）
- 告知用户文件路径
- 提示: "请将文件拖入 Excalidraw (http://localhost:3000)"

### Step 5: 迭代
用户可要求修改，例如：
- "第二个流程图再加一个节点"
- "对比图换个颜色"
- "再加一个时间线图"
```

---

## 执行检查清单

| # | 动作 | 预期结果 |
|---|------|----------|
| 1 | `mkdir -p` 创建目录 | 目录就绪 |
| 2 | 写入 extract.py | 文件创建 |
| 3 | 写入 layout.py | 文件创建 |
| 4 | 写入 open.py | 文件创建 |
| 5 | 写入 excalidraw-schema.md | 文件创建 |
| 6 | 写入 diagram-templates.md | 文件创建 |
| 7 | 写入 SKILL.md | 文件创建 |
| 8 | `pip install python-docx markitdown` | 依赖安装 |
| 9 | 用一篇短文章做 end-to-end 测试 | 生成 .excalidraw 文件可拖入 Excalidraw |
