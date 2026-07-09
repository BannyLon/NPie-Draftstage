# 哌稿场 · 档期 — 全面审计报告

**审计日期**：2026-07-09
**审计范围**：content-os.html (222行) + CSS/content-os.css (953行) + JS/content-os.js (2123行) + CSS/theme-editorial.css (60行)
**总代码量**：3,358 行

---

## 一、总体评价

### 优势

| 维度 | 评价 |
|------|------|
| **产品定位** | 精准——面向自媒体创作者的工作日倒排看板，市面上没有同类工具 |
| **核心算法** | 工作日倒排引擎是真正的壁垒功能，跳过周末+11个法定节假日 |
| **交互设计** | 拖拽即排期、右键上下文感知、双击重命名——操作密度高但不混乱 |
| **视觉系统** | 7 套完整主题 + 暗色模式，CSS 变量驱动的主题切换架构是正确的技术选择 |
| **数据安全** | 纯前端 localStorage + JSON 导出，用户完全掌控数据 |
| **工程架构** | HTML/CSS/JS 三层分离 + 主题独立文件，单文件可部署 |

### 核心价值

> 把"脑子里记住各条选题的制作节点、手动算日期、Excel 列表管理"三件事合为一张看板。创作者只需要拖一下发布日期，所有节点的截止日自动算好。

---

## 二、问题清单

### 🔴 Critical

| # | 问题 | 原因 | 后果 |
|---|------|------|------|
| C1 | **document 事件监听器泄漏** | `bindTimelineEvents()` 每次 render 在 `forEach` 里加 `document.addEventListener('mouseup', ...)`，从不移除。6 条选题 × 10 次 render = 60 个冗余监听器 | 内存持续增长，拖拽响应越来越慢，长时间使用后页面卡顿 |

### 🟠 High

| # | 问题 | 原因 | 后果 |
|---|------|------|------|
| H1 | **localStorage 写入失败无提示** | `save()` 函数 `catch (_) {}` 吞掉所有错误。配额满了用户不知道，数据丢失无感知 | 用户编辑半天，刷新后发现什么都没保存 |
| H2 | **确认弹窗用浏览器原生 `confirm()`** | 无法定制文案格式、按钮文字、样式。体验割裂 | 与精致的看板 UI 完全不搭，降低产品质感 |
| H3 | **无可撤销机制** | 删选题、删节点、移动排期都是不可逆操作 | 误操作后无法恢复，用户挫败感强 |
| H4 | **节假日硬编码 2026 年** | `HOLIDAYS` Set 写死 2026 年日期，2027 年 1 月 1 日起倒排全部错误 | 4 个月后应用核心功能失效 |

### 🟡 Medium

| # | 问题 |
|---|------|
| M1 | **无键盘快捷键** — 纯鼠标操作效率低。高频操作（新建选题、存档、切换视图）应有快捷键 |
| M2 | **导入无数据校验** — `JSON.parse` 后直接替换 `state.topics`，非法数据会导致应用崩溃 |
| M3 | **`setTimeout` 滚动逻辑脆弱** — 多处用 `setTimeout(fn, 50)` 等 DOM 渲染，高负载设备上可能失效 |
| M4 | **无离线/弱网提示** — Tailwind CDN 和 Google Fonts 加载失败时页面完全无样式，用户看到的是乱码 |
| M5 | **save() 调用过于频繁** — 每次勾选、每次拖拽、每次重命名都写 localStorage。应做 debounce |
| M6 | **`contentEditable` 重命名不友好** — 双击即进入编辑，没有视觉提示，容易误触发 |
| M7 | **商单金额无校验** — 可输入任意文本如 "abc" |

### 🟢 Low

| # | 问题 |
|---|------|
| L1 | 无 favicon，浏览器标签页显示默认图标 |
| L2 | Toast 提示在移动端位置偏低，可能被键盘遮挡 |
| L3 | 侧边栏收缩后导入导出按钮排列拥挤 |
| L4 | 无 `aria-label` / 无障碍支持 |
| L5 | 自定义工作流节点数无上限，极端情况下可能创建 100 个节点 |

---

## 三、具体优化建议

### C1 修复方案（事件泄漏）

```javascript
// 将 mouseup 监听器移到 forEach 外部，只绑定一次
let dragState = { active: false, topicId: null };
document.addEventListener('mousedown', e => {
    const label = e.target.closest('.topic-label');
    if (label) { dragState.active = true; dragState.topicId = label.dataset.labelId; }
});
document.addEventListener('mouseup', () => { dragState.active = false; });
```

### H1 修复方案（存储失败提示）

```javascript
function save() {
    try {
        localStorage.setItem('content-os-v2', JSON.stringify(state.topics));
    } catch (e) {
        toast('⚠️ 存储空间不足，请导出备份后清理数据');
        console.error('localStorage quota exceeded', e);
    }
}
```

### H4 修复方案（节假日动态化）

```javascript
const HOLIDAYS = new Set();
// 2026 已知假日
['2026-01-01', '2026-02-17', ...].forEach(d => HOLIDAYS.add(d));
// 每年自动追加春节（简化算法）
function addSpringFestival(year) { /* ... */ }
```

### M5 修复方案（save debounce）

```javascript
let _saveTimer;
function save() {
    clearTimeout(_saveTimer);
    _saveTimer = setTimeout(() => {
        try { localStorage.setItem('content-os-v2', JSON.stringify(state.topics)); } catch(_) {}
    }, 300);
}
```

---

## 四、Top 5 改进事项排序

| 优先级 | 事项 | 影响 | 工作量 |
|--------|------|------|--------|
| **1** | 修复 document 事件泄漏 (C1) | 阻止长期使用后性能退化 | 30min |
| **2** | localStorage 写入失败提示 (H1) | 防止静默数据丢失 | 10min |
| **3** | 节假日动态化/外部配置 (H4) | 确保 2027 年仍可用 | 1h |
| **4** | save() 加 debounce (M5) | 减少不必要的磁盘写入 | 15min |
| **5** | 自定义 confirm 弹窗替代原生 (H2) | 统一产品质感 | 1.5h |

---

## 五、产品战略与下一步迭代建议

### 当前阶段判断

产品处于 **PMF 验证期**。核心功能（工作日倒排 + 选题看板 + 进度追踪）已完成，可以面向真实用户收集反馈。

### 建议迭代路线

| 阶段 | 目标 | 核心功能 |
|------|------|----------|
| **v3.0** 稳定性 | 修复 Critical/High 问题，上线首个可分发版本 | 事件泄漏修复、存储保护、导入校验、错误边界 |
| **v3.1** 协作 | 多人共享看板（可选后端） | JSON 同步到 CloudKit/iCloud、只读分享链接 |
| **v3.2** 平台联动 | 与发布平台打通 | Bilibili 定时发布、公众号草稿箱、YouTube scheduled |
| **v3.3** 智能 | AI 辅助排期 | 根据历史数据推荐最佳发布日期、自动预估各阶段耗时 |
| **v4.0** 商业化 | 付费功能 | 团队版、高级主题、数据看板、API 接入 |

### 风险提示

1. **Tailwind CDN 依赖** — 如果 CDN 不可用，整个应用白屏。建议内联关键 CSS 或提供离线版本
2. **localStorage 上限 5MB** — JSON 选题数据 + 6 套主题 + 自定义工作流，目前远未达到，但导入大文件时需校验
3. **无用户认证** — 看板数据与浏览器绑定，换设备需要手动导出/导入。对重度用户是显著摩擦

---

> **一句话总结**：产品方向清晰、核心算法扎实、交互设计到位。当前最紧迫的是修掉事件泄漏和存储静默失败，然后把节假日做成动态配置，就可以对外分发了。
