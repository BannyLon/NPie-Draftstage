# wechat-automator v1.6.0

> 一站式微信公众号内容资产化引擎 — 把短期流量转化为长期内容复利。

`wechat-automator` 是一个 Claude Code Skill，将**内容深度优化**、**精排版渲染**、**一键推送草稿箱**整合为一条三阶段自动化流水线。说一句「发公众号」，从 Markdown 到草稿箱全部搞定。

---

## 它能做什么

```
你给一个文件 + 说一句「发公众号」
         ↓
  ⓪ 内容优化：脱水 + 结构重组 + 去 AI 味 → 🔴 你确认
  ① 排版渲染：AI 分析文章 → 推荐最佳排版 → 浏览器预览 6 套对比 → 🔴 你选择
  ② 一键发布：上传头图+封面 → 创建草稿
         ↓
  打开公众号后台 → 预览 → 群发 ✅
```

**核心差异化**：不是换颜色的排版工具。6 套异构排版系统各自拥有独立的组件库和视觉语言——同一篇文章用卡片流和杂志流排出来，是两种完全不同的阅读体验。

---

## 快速开始

### 安装

```bash
cp -r wechat-automator/ ~/.claude/skills/wechat-automator/
```

### 可选：设置凭据环境变量

```bash
export WEIXIN_APPID="你的公众号 AppID"
export WEIXIN_APPSECRET="你的公众号 AppSecret"
```

凭据获取：公众号后台 → 开发 → 基本配置。不设环境变量也可以，用到时 Claude 会问你。

### 准备封面和头图

将你的品牌封面图和头图放入 `img/` 目录：

```
img/
├── cover.png         # 推文封面（1080×1080px，1:1）
└── header_image.png  # 正文顶部头图（宽度 677px）
```

两个文件都会被自动上传到微信 CDN 并注入正文。如果缺失，封面会自动生成品牌纯色图 fallback。

### 触发方式

说人话就行：

| 你说的话 | 效果 |
|----------|------|
| 「帮我把这篇排版发公众号」 | 完整三阶段：优化 → 排版 → 上传 |
| 「这个脚本转成推文」 | 同上 |
| 「排版看看效果，先不发」 | 仅排版预览，输出 HTML 文件 |
| 「严格按原文排版发草稿箱」 | 跳过内容修改，仅排版上传 |
| 「用暖色系排版发公众号」 | 自动匹配主题（如 amber） |

### 豁免内容修改

用以下关键词跳过优化阶段（排版仍执行）：

`一字不改` `原封不动` `严格按原文` `不要修改内容` `仅排版` `只排版` `纯排版`

---

## 三阶段工作流

### ⓪ 内容优化（可豁免）

1. **脱水**：去冗余、提论点、压密度（信息密度 +30-50%）
2. **重组**：钩子开头 + 正文骨架 + CTA 结尾
3. **去 AI 味**：调用 humanizer-zh 审阅

🔴 优化完成后暂停，等你确认内容。

### ① 排版渲染（始终执行）

AI 深度理解文章内容 → 关键词匹配分析 → 推荐最佳排版系统 → 生成浏览器预览页（6 套并排对比）→ 你选择 → 渲染 inline HTML。

### ② 一键发布（按需执行）

`upload.py` 自动完成：上传头图到 CDN → 注入正文顶部 → 底部留白 → 上传封面 → 创建草稿 → 返回 media_id。

---

## 6 套异构排版系统

每套不是换颜色，是换一整套组件库和视觉语言：

| 系统 | 设计基因 | 独有组件 | 参考 |
|------|---------|---------|------|
| `classic` 经典左线 | 左粗线分区 | `.golden-quote` `.card-item` `.highlight-box` | 咨询报告 |
| `cardflow` 卡片流 | 每段独立成卡 | `.section-card` `.info-card` `.data-badge` | Notion |
| `editorial` 杂志流 | 大标题+引题 | `.lead` `.ornament-divider` `.image-frame` | The Atlantic |
| `guide` 手册流 | 步骤编号+提示框 | `.step-num` `.tip-box` `.warn-box` `.checklist-item` | 操作指南 |
| `letter` 书信流 | 日期+署名极简 | `.dateline` `.greeting` `.sign-off` `.postscript` | Substack |
| `workshop` 极客流 | 深色实验台+Prompt 卡 | `.prompt-card` `.tool-badge` `.workflow-step` | 开发者笔记 |

### 预设组合

| 预设 | 布局 | 配色 | 适用 |
|------|------|------|------|
| `teal` | classic | teal-gold 青蓝金 | 通用深度分析 |
| `navy` | editorial | navy-coral 深蓝珊瑚 | 商业/行业评论 |
| `forest` | guide | forest-amber 森语琥珀 | 教程/操作指南 |
| `plum` | cardflow | plum-sage 梅紫灰绿 | 产品/工具介绍 |
| `slate` | letter | slate-rose 岩灰玫瑰 | 个人随笔/故事 |
| `amber` | workshop | forest-amber 森语琥珀 | 技术/AI/编程 |

### 使用

```bash
# 预设
build_inline.py in.html out.html --theme navy

# 自由混搭（6×5=30 种）
build_inline.py in.html out.html --layout workshop --palette navy-coral

# 自定义颜色
build_inline.py in.html out.html --theme "#e63946"
```

---

## 微信兼容性

基于生产环境实测得出的硬约束：

| 规则 | 原因 |
|------|------|
| 零 `<style>` 标签 | 微信完全删除 |
| 零 `class` 属性 | 微信完全剥离 |
| 零 `<div>` 元素 | 微信转为裸 `<p>` |
| 全 `style=""` 内联 | 唯一可靠方式 |
| 纯色背景 | `linear-gradient` 会被删除 |
| 禁止 `<pre>` | 换行全部丢失 |
| `<blockquote>` ≤300 字 | 微信有隐性字数上限 |

所有约束已内建在 `build_inline.py` 的验证逻辑中，输出自动检查。

---

## 配图支持

Skill 不内置配图生成（零外部依赖）。但 HTML 结构支持配图占位：

```html
<p class="illustration"><img src="PLACEHOLDER" alt="配图说明"></p>
```

配图准备好后替换 `PLACEHOLDER` 为微信 CDN URL 即可。`.illustration` 样式已内置在所有排版系统中。

---

## 与其它 Skill 协作

```
oral-stylizer → wechat-automator → humanizer-zh
（口述整理）    （排版发布）        （去 AI 味）
```

三者都是软依赖——有则调用，无则跳过。

---

## 文件结构

```
wechat-automator/
├── SKILL.md                  # Skill 定义（三阶段流水线 + 铁律 + 技术规范）
├── README.md                 # 本文件
├── img/
│   ├── cover.png             # 推文封面
│   └── header_image.png      # 正文头图
├── output/
│   ├── article-class-html.html   # （中间产物）class-based HTML
│   ├── article-inline.html       # （中间产物）微信兼容 inline HTML
│   └── theme-preview.html        # （生成物）6 套排版浏览器预览页
└── scripts/
    ├── build_inline.py       # 排版引擎：Layout×Palette → inline HTML
    ├── preview_themes.py     # 预览生成器：6 套并排对比网页
    └── upload.py             # 上传工具：头图+封面+草稿箱
```

---

## 依赖

- Python 3.8+
- `requests`：`pip install requests`
- 一个已认证的微信公众号（AppID + AppSecret）

---

## 许可证

MIT
