# CLAUDE.md — 哌稿场 · 档期 开发规范

## 项目结构

```
NPie_Draftstage/
├── content-os.html          # HTML 骨架（禁止在此写 CSS/JS）
├── CSS/
│   ├── content-os.css       # 核心样式
│   └── theme-editorial.css  # 蓝黄杂志风（独立主题示例）
├── JS/
│   └── content-os.js        # 全部逻辑
├── IMG/                     # 图标/图片资源
├── CLAUDE.md                # 本文件
└── README.md
```

## 红线规则

### 1. 修改 DOM 选择器必须全局搜索
任何 HTML 结构的 class/id 变更，**必须先 `grep` 全项目**查找所有引用位置（CSS 选择器 + JS querySelector），同步更新。禁止只改 HTML 不改 JS/CSS。

### 2. 破坏性操作必须 saveNow()
删除、存档、移动排期、新建选题等**不可逆操作**调用 `saveNow()`（同步写 localStorage），不允许用 debounce 的 `save()`。

### 3. 弹窗禁止点击外部关闭
所有 `modal-overlay` 的 click-outside-to-close **已全部移除**。新增弹窗时也不要加这个行为，防止用户误触丢失输入内容。

### 4. 日期格式化用本地时间
```js
function fmt(d) { return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); }
```
**禁止用 `toISOString()`**——UTC 时区会导致中国时间偏移一天。

### 5. 数据加载优先级
`load()`: localStorage（同步写入最新）→ IndexedDB（回退）→ seedData（空数组）。
**禁止 IndexedDB 优先**，因为 async 写入可能未完成。

### 6. 跑马灯状态不交叉
筛选规则见 `isTopicUrgent()`，权重见 `tickerWeight()`。紧急标记、星评、商单金额、临近天数四维排序。

### 7. debounce save 只用于高频操作
- `save()`：200ms debounce，用于勾选复选框、添加前置准备
- `saveNow()`：即时写入，用于删除/存档/移动/新建

## 主题系统

- 7 套配色 + 暗色模式，均通过 `[data-theme="xxx"]` CSS 选择器覆盖变量
- 新增主题可独立 CSS 文件（参考 `theme-editorial.css`）
- 暗色模式下主题选项灰度不可选（`updateModeUI()`）
- 选题卡背景/组件用 `--card-self`/`--card-commercial`/`--card-comp-local`

## 已知易错点

| 场景 | 陷阱 |
|------|------|
| 改 HTML 内的 class/id | 必须同步搜 JS 里的 querySelector |
| 任务块和日历格是兄弟节点 | `stopPropagation` 无法阻止兄弟事件，需 `e.target.closest('.task-block')` |
| 同日多任务堆叠 | 用渲染期 `Map<taskId, topPx>`，**禁止**修改 state 中的 task 对象 |
| 自定义工作流节点 | 角标统一用"定"字；颜色用行内 `background:${task.color}`（内置仍用 CSS 类兼容暗色模式） |
| localStorage → IndexedDB | `idbSave` 异步，不可靠；`saveNow` 先 localStorage 同步 |
| `showConfirm` 回调 | 不可覆盖 `_confirmCallback` |

## 版本回滚

```bash
git log --oneline | head -20        # 查看历史
git checkout v4.14 -- .             # 回退到指定版本
```
