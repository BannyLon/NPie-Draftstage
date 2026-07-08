# 🐍 Snake English · 英语贪吃蛇

一个把「贪吃蛇」和「英语单词学习」结合的纯前端小游戏。
吃到食物 → 弹出单词卡（音标 / 释义 / 例句 / TTS 发音）→ 学完继续。

零依赖、可离线（PWA）、深浅双主题、支持键盘 / WASD / 触屏滑动 / 方向键。

## ✨ 功能

- 经典贪吃蛇玩法（撞墙 / 撞自己结束）
- 吃到食物弹出单词卡：音标、英文释义、例句、Web Speech 朗读
- **加权复习**：点「再练一下」会让该词在后续更可能出现（不会无限增长数组）
- JSON 词库导入（自定义你的单词表）
- 分数 / 最佳成绩 / 已学数 本地持久化（localStorage）
- 主题：深色 / 浅色 / 跟随系统，高对比度，减少动画
- 语音：美音 / 英音、语速 / 音调调节
- PWA：可安装、可离线（Service Worker 缓存）
- 响应式：桌面、平板、手机自适应，手机端有触屏方向键

## 🚀 运行

纯静态站点，三种方式任选：

```bash
# 方式 1：Python（最简单）
python3 -m http.server 8000
# 打开 http://localhost:8000

# 方式 2：Node
npx serve .

# 方式 3：直接双击 index.html
# （注意：Service Worker 需要 http(s)，直接打开文件时离线/安装功能不可用，其它正常）
```

## 🎮 操作

| 操作 | 键盘 | 触屏 |
|------|------|------|
| 移动 | 方向键 / WASD | 画布滑动 或 屏幕底部方向键 |
| 暂停/继续 | 空格 | 「暂停」按钮 |
| 开始 / 再来一局 | — | 「开始」按钮（游戏结束后变为「↻ 再来一局」）|

## 📥 自定义词库

点击「📥 导入词库」选择 JSON 文件即可。格式（数组，每项一个单词）：

```json
[
  {
    "word": "resilient",
    "ipa": "/rɪˈzɪliənt/",
    "definition": "able to quickly return to a previous good condition",
    "examples": ["Children are often very resilient."]
  },
  {
    "word": "concise",
    "def": "giving a lot of information clearly and in a few words",
    "examples": ["Please be concise in your answer."]
  }
]
```

字段说明：

| 字段 | 必填 | 说明 |
|------|------|------|
| `word` | ✅ | 英文单词 |
| `definition` 或 `def` | ✅ | 英文释义（两者任填其一） |
| `ipa` | ❌ | 音标 |
| `examples` | ❌ | 例句数组（字符串数组） |

模板见 [`vocab-template.json`](./vocab-template.json)，也可在「❓ 词库说明」弹窗里下载。

## 📁 项目结构

```
english-snake/
├── index.html          页面结构与弹窗
├── main.js             游戏逻辑 + 渲染 + TTS + 设置
├── styles.css          样式（深/浅主题、响应式）
├── manifest.json       PWA 清单
├── sw.js               Service Worker（离线缓存）
├── vocab-template.json 词库导入模板
├── icon.svg            矢量图标
├── icon-192.png        PWA 图标 192×192
├── icon-512.png        PWA 图标 512×512
└── tools/
    └── make_icons.py   用标准库生成 PNG 图标的脚本
```

## 🔧 重新生成图标

图标用 Python 标准库手绘（无第三方依赖），需要修改时：

```bash
python3 tools/make_icons.py
# 重新生成 icon-192.png 和 icon-512.png
```

设计：深色圆角方形背景 + 青→紫渐变蛇身 + 蛇头/眼睛 + 发光食豆。
源矢量见 [`icon.svg`](./icon.svg)。

## 🛠 技术栈

原生 HTML / CSS / JavaScript，无框架、无构建步骤。
- 渲染：Canvas 2D（渐变蛇身、发光食物、粒子特效）
- 发音：Web Speech API（`SpeechSynthesis`）
- 持久化：localStorage
- 离线：Service Worker + Cache Storage

## 📝 说明

- 发音依赖浏览器的 Web Speech API 与系统语音包；不同系统可用语音可能不同。
- 「音效」「背景音乐」开关为预留项，当前版本尚未接入实际音频。
