# 哌稿场 · 档期 (NPie Draftstage) — 完整开发 Prompt

> 将此 prompt 交给任意 AI 编码工具，应能复现功能完全一致的应用。

---

## 一、项目概述

开发一个名为「**哌稿场 · 档期**」（英文 NPie Draftstage）的**内容创作排期管理看板**。这是一个单页面浏览器应用，帮助自媒体创作者管理从选题策划到发布的全流程。

**核心能力：** 选题管理 → 工作日倒排 → 日历可视化 → 进度追踪 → 存档归档。

---

## 二、技术约束

- **纯前端**：HTML + CSS + JS，零构建工具，零框架
- **三层分离**：`content-os.html`（骨架）、`CSS/content-os.css`（样式）、`JS/content-os.js`（逻辑）
- CDN 依赖：Tailwind CSS（`https://cdn.tailwindcss.com`）+ Google Fonts（Inter 400/500/600/700/800 + Noto Sans SC 400/500/700）
- 数据持久化：`localStorage`
- 支持 Chrome / Edge / Safari / Firefox

---

## 三、文件结构

```
NPie_Draftstage/
├── content-os.html       # HTML 骨架
├── CSS/
│   └── content-os.css    # 全部样式
├── JS/
│   └── content-os.js     # 全部逻辑
├── IMG/
│   ├── NPIEAI_logo.jpg   # 品牌 Logo（36px高）
│   ├── Obsidian.webp     # Obsidian 跳转图标（22px高）
│   ├── Export.svg        # 导出图标（18px）
│   ├── Import.svg        # 导入图标（18px）
│   ├── About.svg         # 关于图标（16px）
│   └── Settings.svg      # 设置图标（16px）
├── README.md
└── prompt.md
```

---

## 四、页面布局

### 整体结构
```
┌──────────────┬─────────────────────────────────────────┐
│   Sidebar    │  Main Panel                            │
│  (260px)     │  ┌───────────────────────────────────┐ │
│              │  │  Header: 跑马灯 + Logo + 品牌名    │ │
│  Brand Logo  │  ├───────────────────────────────────┤ │
│  + 名称      │  │  Timeline Hero + Calendar         │ │
│              │  │  + 角标图例 + 增加选题按钮         │ │
│  Nav 导航    │  ├───────────────────────────────────┤ │
│              │  │  Topic Cards Grid (2列)           │ │
│  选题目录    │  │                                   │ │
│  (自适应)    │  └───────────────────────────────────┘ │
│              │                                        │
│  导出/导入   │                                        │
│  + 说明      │                                        │
│              │                                        │
│  关于/设置   │                                        │
│  + Slogan    │                                        │
└──────────────┴─────────────────────────────────────────┘
```

### Sidebar（左侧栏，260px，可折叠至 56px）
1. **Brand 区**：Logo 34px圆角 + "NPie Draftstage"（0.7rem金色）+ "哌稿场 · 档期"（1.28rem粗体）
2. **折叠按钮**：`◀`/`▶` 箭头，右上角绝对定位
3. **Nav 导航**：排期日历 / 选题卡 / 已存档 三个按钮（`.nav-pill`）
4. **选题目录**：自适应高度（`max-height: calc(100vh - 540px)`），超过可滚动。每项显示类型角标（红底"自"/金底"商"）+ 名称 + 紧急橙色左边框
5. **Section 1**：导出备份 + 导入恢复按钮（图标+文字）+ 功能说明文字
6. **Section 2**（始终吸底）：关于嗯哌 + 设置按钮（并排）+ Slogan（`text-align: justify` 首尾对齐）

### Main Panel（右侧主区域）
1. **Header Bar**：左侧跑马灯（flex:1）+ 右侧 Logo + "哌稿场 · 档期 / NPie Draftstage"
2. **Timeline Section**：Hero 描述 + 横向滚动日历 + 底部"增加选题"按钮 + 角标图例
3. **Topics Section**：标题 + 描述 + 选题卡片网格（2列，响应式）

---

## 五、数据模型

### Topic（选题）
```js
{
  id: string,           // 唯一ID，如 't1'
  title: string,        // 选题名称
  publishDate: string,  // 发布日期 'YYYY-MM-DD'
  type: string,         // 工作流类型ID：'self' | 'commercial' | 自定义ID
  status: string,       // 'normal' | 'important' | 'urgent'
  priority: number,     // 影响力 0-5 星
  budget: string,       // 金额（仅商单显示）
  obsidianUrl: string,  // Obsidian 笔记链接
  archived: boolean,    // 是否已存档
  prep: [{ text: string, completed: boolean }],  // 前置准备清单
  tasks: [{             // 制作流程节点
    id: string,         // 阶段ID
    name: string,       // 阶段名称
    days: number,       // 工作天数
    color: string,      // 背景色
    completed: boolean, // 是否完成
    startDate: string,  // 开始日期
    endDate: string     // 结束日期
  }]
}
```

### State
```js
{
  topics: Topic[],
  selectedTopicId: string|null,
  viewStart: Date,      // 7月1日
  viewEnd: Date,        // 12月31日，随选题扩展
  activeNav: string,    // 'timeline' | 'topics' | 'archived'
  drag: object|null,
  sidebarCollapsed: boolean
}
```

---

## 六、工作流系统

### 内置工作流
**自制内容（self）：**
前置准备(1天) → 脚本(1天) → A-roll(1天) → B-roll(1天) → 剪辑(2天) → 包装(1天) → 封面/文案/发布（发布日堆叠）

**商单（commercial）：**
收到并拆解 Brief(2天) → 完成脚本大纲(3天) → 品牌审核(2天) → 脚本(1天) → A-roll(1天) → B-roll(1天) → 剪辑(2天) → 包装(1天) → 封面/文案/发布（发布日堆叠）

### 倒排算法（核心）
- **输入**：发布日期
- **输出**：每个阶段的工作日日期区间
- **规则**：
  - 封面/文案/发布固定在发布日当天（三个块垂直堆叠）
  - 其余阶段从发布日向前倒推
  - 每个阶段占 N 个工作日
  - 跳过周末（周六日）和法定节假日
  - `prevBusinessDay(date)`：找 date 之前最近的工作日
  - `subtractBusinessDays(date, n)`：向前减 n 个工作日
  - 法定节假日：2026年元旦/春节/清明/劳动节/端午/中秋/国庆，存储为 `Set<string>`（'YYYY-MM-DD'格式）

### 自定义工作流
- 设置弹窗 → 工作流面板 → 新增
- 填写名称 + 添加节点（名称/天数/颜色）
- 系统自动在末尾追加封面/文案/发布三个节点
- 新增选题的类型下拉框自动出现自定义工作流
- 内置工作流可编辑不可删除，自定义可删除（有进行中选题时阻止）
- 数据存 `localStorage` key: `npiedraft-custom-wf`

---

## 七、核心交互

### 排期日历
| 操作 | 行为 |
|------|------|
| 拖拽左侧选题标签到日期格子 | `moveWholeSchedule`：以该日期为新发布日，重新按工作日倒排整条选题 |
| 拖拽右侧任务块到日期格子 | `moveSingleTask`：仅移动该节点到目标日期 |
| 右键日期格子（空格子） | 弹出"＋ 新增日程"菜单 |
| 右键日期格子（有任务） | 弹出"删除「节点名」"菜单 |
| 右键选题卡 | 弹出选题操作菜单（按进度：放弃/存档/恢复/彻底删除） |
| 双击任务块 | `contentEditable` 原地重命名 |
| 选中选题后点击日期格子 | **无效**（已移除 click 移动，仅拖拽） |

### 选题卡
- 左上角类型角标：红圈"自" / 金圈"商"
- 紧急选题橙色左边框（规则见跑马灯）
- Obsidian 图标：灰色未设置，点击弹窗输入URL，设置后变亮，点击跳转
- 前置准备：输入框 + 添加按钮 + 勾选删除
- 制作流程：两列网格，复选框勾选 → 进度条联动
- 工作流类型下拉切换 → 重建排期
- 右键菜单：重命名 / 放弃(0%) / 存档(100%) / 恢复 / 彻底删除

### 进度计算
```js
progress = (prep中completed + tasks中completed) / (prep总数 + tasks总数) × 100%
```

### 跑马灯（顶部通知滚动条）
- **进入条件**（`isTopicUrgent`）：
  - 状态=紧急 → 始终显示
  - 状态=重要 / 影响力≥4星 / 商单有金额 → 距发布≤7天
  - 自制≤3天 / 商单≤5天
- **排序**（`tickerWeight`）：紧急+200 / 重要+80 / 每星+15 / 商单金额+40 / 金额≥10万+30 / 金额≥1万+15 / 临近度+50-5×天数
- 内容示例：`🔥 自制 · 选题名★★★ [¥50,000] — 2天后发布`
- CSS 动画无缝循环，hover 暂停

### 右键菜单
- 选题级（日历格子/选题卡触发）：按进度和存档状态动态显示
- 节点级（任务块触发）：删除该节点
- 空格子（日历格子触发）：新增日程

---

## 八、弹窗系统

| 弹窗 | 触发 | 内容 |
|------|------|------|
| 新增选题 | "+ 增加选题"按钮 | 名称/工作流类型/日期/状态(单选)/影响力(五星)/金额(商单显示) |
| 新增日程 | 右键空格子 → 新增日程 | 日程名称 |
| Obsidian链接 | 点击Obsidian图标 | URL输入框 + 取消/清除/确认 |
| 重命名选题 | 右键选题 → 重命名 | 名称输入 |
| 设置 | 侧栏设置按钮 | 三Tab：外观/主题/工作流 |

---

## 九、主题系统

### 模式
- 日间 ☀️ / 夜间 🌙，存 `localStorage` key: `npiedraft-mode`
- CSS：`[data-theme="dark"]` 覆盖所有 CSS 变量
- 暗色模式下：任务块13种stage各有暗色背景+浅色文字覆盖、侧栏选题/日历标签底色强制 `!important`、主题选项灰度不可选

### 六套配色
| 主题 | data-theme | 基调 |
|------|-----------|------|
| 暖棕（默认） | warm | 米色底 + 金棕强调 |
| 冷灰 | cool | 灰白底 + 蓝灰强调 |
| 自然绿 | green | 浅绿底 + 森林绿强调 |
| 高级时尚杂志风 | magazine | 暖白底 + 铜色强调 |
| 草绿小清新风 | fresh | 浅绿底 + 翠绿强调 |
| 暖金 | warmgold | 奶油底 + 金色强调 |

主题存 `localStorage` key: `npiedraft-theme`。所有颜色通过 CSS 自定义属性定义（`--bg`, `--surface`, `--text`, `--accent` 等 ~13 个变量）。

---

## 十、其他细节

### Toast 提示
固定在页面底部居中，`border-radius: 99px` 胶囊形，2.4秒自动消失。

### 折叠侧栏
`state.sidebarCollapsed`，展开 260px → 收缩 56px。收缩后：仅显示折叠按钮 + 品牌logo（小）+ 导入导出图标 + 关于设置图标（上下排列）+ 隐藏所有文字。

### localStorage Key 清单
| Key | 内容 |
|-----|------|
| `content-os-v2` | 选题数据 JSON |
| `npiedraft-mode` | 'light'/'dark' |
| `npiedraft-theme` | 'warm'/'cool'/'green'/'magazine'/'fresh'/'warmgold' |
| `npiedraft-custom-wf` | 自定义工作流 JSON |

### 导出/导入
- 导出：`JSON.stringify({ topics: state.topics })` → Blob → 下载
- 导入：FileReader → JSON.parse → 合并到 state.topics → 重新渲染

### 兼容性
- `load()` 函数处理旧数据字段缺失（`archived`/`obsidianUrl`/`status`/`priority`/`budget` 默认值）
- v2.0 迁移：旧 `edit1`/`edit2` → 新 `edit`，完成状态 OR 合并

---

## 十一、CSS 设计规范

### 设计令牌（CSS 变量）
- `--bg`：页面底色
- `--surface`：卡片/面板底色
- `--surface-muted`：次级底色
- `--border`：边框色
- `--text`：主文字色
- `--text-muted`：次要文字色
- `--muted-2`：更淡文字色
- `--accent`：强调色（金色系）
- `--accent-soft`：柔和强调色
- `--green`/`--red`/`--blue`/`--yellow`：语义色
- `--shadow`：卡片阴影

### 任务块颜色（13种 stage）
```css
stage-prep/research: 暖米色
stage-script:        浅红
stage-a_roll:        浅绿
stage-b_roll:        浅蓝灰
stage-edit:          浅金黄
stage-package:       暖灰
stage-cover/copy:    浅暖灰
stage-publish:       深玫瑰（白字）
stage-brief:         浅棕
stage-outline:       浅褐
stage-review:        浅紫
stage-custom:        淡紫
```

### 关键尺寸
- Sidebar：260px → 收缩 56px
- Timeline 行高：90px
- 日期单元格：58–150px（根据任务名自适应）
- 选题卡：2列网格，响应式断点 1100px/768px
- 字体：中文 Noto Sans SC，英文/数字 Inter
- 基础字号：body 继承，任务块 0.68rem，选题目录 0.74rem

---

## 十二、交互状态颜色
- 类型角标：自制 `#C5554A`（红）/ 商单 `#C89B3C`（金）
- 紧急标注：`#E04030`（鲜红圆点）/ `#E08840`（橙色左边框）
- 完成状态：`opacity: 0.45` + `text-decoration: line-through`
- 选中态：`outline: 2px solid rgba(176,138,83,0.5)`
- Hover：`filter: brightness(0.94)` 或背景加深

---

## 十三、注意事项

1. **日期格式化**：必须使用本地时间 `getFullYear()/getMonth()/getDate()`，**禁止**使用 `toISOString()`（会导致 UTC 时区偏移一天）
2. **事件冒泡**：任务块和日期格子是兄弟节点，`stopPropagation` 无法阻止兄弟元素事件，需在 cell click 中检查 `e.target.closest('.task-block')`
3. **堆叠逻辑**：同日多任务用渲染期 `Map<taskId, topPx>` 计算行内样式，**绝不**修改 state 中的 task 对象
4. **跑马灯**：内容列表复制一份实现无缝循环，CSS `@keyframes translateX(-50%)`
5. **星星评分**：CSS `clip-path: polygon(...)` 画五角星，点击切换 `active` 类
