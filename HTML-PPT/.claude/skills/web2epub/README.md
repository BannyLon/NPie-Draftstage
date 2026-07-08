# Web → EPUB → 微信读书

> **版本**: v2.0.0 | **开发者**: 嗯哌AI

一键将网页/博客/文章或本地文档（Word/PDF/TXT）转换为排版干净的 EPUB 电子书，并自动上传到微信读书（WeRead）书架。

## 决策树（核心流程）

```
用户输入
  │
  ├─── URL ──────────────────────────────────────────────┐
  │                                                      │
  │   fetch_article.py 抓取 + 检测语言                    │
  │       │                                              │
  │       ├─ 正文是全英文 ──→ 询问用户:                   │
  │       │                    "检测到外文内容，           │
  │       │                     是否需要翻译为中文？"     │
  │       │                       │                      │
  │       │                  ┌────┴────┐                 │
  │       │              不需要      需要                │
  │       │                  │         │                 │
  │       │                  │   询问用户:                │
  │       │                  │   "仅保留中文，             │
  │       │                  │    还是中英对照？"          │
  │       │                  │     │                      │
  │       │                  │  ┌──┴───┐                  │
  │       │                  │ 仅中文 中英对照             │
  │       │                  │    │     │                 │
  │       │                  └────┼────┘                 │
  │       │                       ↓                      │
  │       ├─ 正文是中文 ──────→ 直接进行                  │
  │       │                       ↓                      │
  │       └─ 正文为空/失败 ───→ 报错 + 让用户提供内容      │
  │                                                      │
  ├─── 本地文件 (.txt/.pdf/.doc/.docx/...) ──────────────┤
  │   直接转换（不询问翻译，用户对自己的文件负责）            │
  │                                                      │
  └─── 多链接批量 ────────────────────────────────────────┘
                            ↓
                    build_epub.sh 生成EPUB
                            ↓
                    upload_weread.py 上传微信读书书架
                            ↓
                         完成 ✓
```

## 前置条件

```bash
# 基础工具
brew install pandoc
pip3 install trafilatura beautifulsoup4 requests openai chardet

# 上传需要 Playwright
pip3 install playwright
playwright install chromium
```

## 使用场景

### 场景一：丢来一个 URL

**Step 1 — 抓取内容**

```bash
python3 scripts/fetch_article.py "https://example.com/article" > article.json
```

返回字段：`title`、`author`、`date`、`text`（Markdown）、`needs_translation`

**Step 2 — 检查语言，决定翻译**

- `needs_translation: false`（正文是中文）→ 直接去 Step 3
- `needs_translation: true`（外文）→ 询问用户：
  - "检测到外文内容，是否需要翻译为中文？"
  - **不需要** → 直接去 Step 3
  - **需要** → 追问："仅保留中文，还是中英对照？"
    - **仅中文** → 翻译后替换原文
    - **中英对照** → 原文 + 译文按段落交错排列

```bash
export OPENAI_API_KEY="sk-..."
echo "$MARKDOWN_TEXT" | python3 scripts/translate.py "en" > translated.md
```

**Step 3 — 生成 EPUB**

```bash
TITLE=$(python3 -c "import json; print(json.load(open('article.json'))['title'])")
AUTHOR=$(python3 -c "import json; print(json.load(open('article.json'))['author'])")
python3 -c "import json; print(json.load(open('article.json'))['text'])" > article.md

bash scripts/build_epub.sh \
  -i article.md \
  -o "${TITLE}.epub" \
  -t "$TITLE" \
  -a "$AUTHOR"
```

**Step 4 — 上传微信读书**

```bash
python3 scripts/upload_weread.py "${TITLE}.epub"
```

### 场景二：丢来一个本地文件

支持格式：`.docx` `.pdf` `.txt` `.md` `.html` `.epub` `.mobi` `.azw3` `.fb2` `.rtf`

**直接转换 + 上传，不询问翻译。**

```bash
bash scripts/build_epub.sh \
  -i ~/Downloads/report.docx \
  -o "报告.epub" \
  -t "报告标题" \
  -a "作者"

python3 scripts/upload_weread.py "报告.epub"
```

### 场景三：多链接批量

每个 URL 独立执行场景一的完整流程。除非用户明确要求合并，否则每链接单本 EPUB。

## 脚本参考

### `fetch_article.py` — 网页内容提取

```bash
python3 scripts/fetch_article.py "https://..."
# → {"title":"...", "author":"...", "text":"...", "needs_translation":true/false}
```

- 基于 trafilatura，自动适配 precision/recall
- 自动判断语言，标记 `needs_translation`
- 输出 Markdown 格式正文

### `translate.py` — 外文翻译

```bash
export OPENAI_API_KEY="sk-..."
cat article.md | python3 scripts/translate.py "en" > translated.md
```

- 默认模型 `gpt-4o-mini`，支持 `OPENAI_BASE_URL` 自定义 API
- 6K 字符分块，保留 Markdown 格式

### `build_epub.sh` — EPUB 生成

```bash
bash scripts/build_epub.sh \
  -i input.md \
  -o output.epub \
  -t "标题" \
  -a "作者" \
  [--css custom.css]
```

- 自动识别 .md/.docx/.pdf/.txt/.html 等格式
- 内置微信读书优化 CSS（衬线字体、中文排版、代码块）
- 自动生成目录（TOC）

### `upload_weread.py` — 微信读书上传

使用 Playwright 浏览器自动化上传：

```bash
python3 scripts/upload_weread.py --check   # 检查登录状态
python3 scripts/upload_weread.py book.epub # 上传文件
```

上传流程：打开 `weread.qq.com/web/upload` → 自动选文件 → 浏览器执行腾讯云 COS 分片上传 → 通知服务器 → 书架可见。

支持格式：`.epub` `.pdf` `.txt` `.doc` `.docx` `.mobi` `.azw3` `.fb2` `.rtf` `.lit` `.cbr` `.cbz`

## Cookie 配置

```bash
# 手动获取一次，保存后即可自动上传
~/.web2epub/weread_cookies.json
```

获取：Chrome 打开 https://weread.qq.com → 微信扫码登录 → F12 → Application → Cookies → 提取 `wr_vid`、`wr_skey`、`wr_rt`

Cookie 会过期（数天到数周），过期后 `--check` 会提示，重新获取即可。

## 微信读书限制

| 限制项 | 说明 |
|--------|------|
| 非付费会员 | 每月约 3 本导入额度（2024年起） |
| 付费会员 | 无限制或更高额度 |
| 单文件大小 | 最大 50MB |
| 笔记可见性 | 默认为私密 |

## 架构

```
web2epub/
├── README.md                    # 本文档
├── SKILL.md                     # Claude Code skill 定义（含决策树）
├── references/
│   └── weread-setup.md          # WeRead 配置指南
└── scripts/
    ├── fetch_article.py         # 网页内容提取 + 语言检测
    ├── translate.py             # 外文→中文翻译
    ├── build_epub.sh            # 多格式→EPUB 转换
    ├── upload_weread.py         # 微信读书上传（Playwright）
    └── weread_login.py          # 登录辅助工具
```

## 更新日志

### v2.0.0 (2026-06-28)
- 重写上传机制：废弃旧 POST 接口，改用 Playwright + 腾讯云 COS 分片上传
- 新增翻译决策流程：URL 检测语言 → 询问翻译/仅中文/中英对照
- 本地文件直接转换，不询问翻译
- 去除 pandoc 警告

### v1.0.0
- 初始版本：fetch → translate → build → upload
- 基于 Cookie 的简单 HTTP POST 上传
