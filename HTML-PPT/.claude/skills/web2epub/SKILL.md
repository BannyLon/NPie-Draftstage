---
name: web2epub
version: 2.0.0
author: 嗯哌AI
description: >-
  一键将网页/博客/文章或本地文档（Word/PDF/TXT）转换为排版干净的 EPUB 电子书，并可自动上传到微信读书（WeRead）书架。
  使用此技能的场景包括但不限于：
  (1) 用户丢来一个 URL 说"帮我看这篇文章"或"转成电子书"；
  (2) 用户丢来一个 .docx/.pdf/.txt 文件说"帮我转成 EPUB"；
  (3) 用户说"放到微信读书上"或"导入微信读书书架"；
  (4) 用户提到外文内容需要翻译成中文；
  (5) 用户说"保存这篇博客/文章到微信读书"。
  无论用户给出的输入是 URL 还是文件路径，只要最终目标是 EPUB/电子书/微信读书，都应触发此技能。
---

# Web → EPUB → 微信读书

> **v2.0.0** · 开发者：嗯哌AI

将任意网页、博客、文档（Word/PDF/TXT）一键转换为排版干净的 EPUB 电子书，自动上传到微信读书书架。

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

## 前置条件检查

使用此 skill 前先检查以下工具是否可用：

```bash
which pandoc python3
pip3 list 2>/dev/null | grep -iE "trafilatura|beautifulsoup|requests"
```

如果缺 `pandoc` 或 Python 包，先安装：

```bash
# pandoc
brew install pandoc

# Python 包
pip3 install trafilatura beautifulsoup4 requests chardet

# 上传需要
pip3 install playwright
playwright install chromium
```

## 输入处理

### 场景一：用户丢来一个 URL

1. **抓取内容**

```bash
python3 scripts/fetch_article.py "https://example.com/article" > article.json
```

返回 JSON，包含 `title`、`author`、`date`、`text`(Markdown格式)、`needs_translation`。

2. **检查 `needs_translation` 字段**

- **`false`**（正文是中文）→ 直接进入 EPUB 生成
- **`true`**（正文是非中文）→ **必须询问用户**："检测到外文内容，是否需要翻译为中文？"
  - 用户说**不需要** → 直接进入 EPUB 生成（保留原文）
  - 用户说**需要** → 继续追问："仅保留中文，还是中英对照？"
    - **仅中文** → 翻译后替换原文，进入 EPUB 生成
    - **中英对照** → 将翻译内容以对照格式拼入原文，进入 EPUB 生成

3. **翻译执行**

```bash
export OPENAI_API_KEY="sk-..."  # 如未配置则提示用户
echo "$MARKDOWN_TEXT" | python3 scripts/translate.py "en" > translated.md
```

中英对照格式：每个段落原文在上、译文在下（用 blockquote 区分），或按章节交替。

### 场景二：用户丢来一个本地文件

支持格式：`.docx` `.pdf` `.txt` `.md` `.html` `.epub` `.mobi` `.azw3` `.fb2` `.rtf`

**直接转换**，不询问翻译。用户对自己的文件负责，他要传什么就传什么。

```bash
bash scripts/build_epub.sh \
  -i ~/Downloads/report.docx \
  -o output.epub \
  -t "标题" \
  -a "作者"
```

### 场景三：多个链接批量处理

对每个 URL 独立执行完整的场景一流程。除非用户明确要求合并，否则每个链接生成本单独的 EPUB。

## 生成 EPUB

```bash
bash scripts/build_epub.sh \
  -i input.md \
  -o output.epub \
  -t "文章标题" \
  -a "作者"
```

脚本会自动：
- 根据文件扩展名选择正确的 pandoc 输入格式
- 应用微信读书友好的 CSS 排版（衬线字体、适当行距、代码块样式等）
- 生成目录（TOC）
- 设置中文语言元数据

### 质量控制

```bash
pandoc output.epub -t plain --quiet 2>/dev/null && echo "✓ EPUB 有效"
```

### ⚠️ 血的教训：编码问题导致乱码

**这是最常见的错误，必须检查。**

中文 TXT 文件的编码往往是 **GBK / GB18030 / Shift-JIS**，而不是 UTF-8。如果直接用 pandoc 读取非 UTF-8 的 TXT，生成的 EPUB 全是乱码。

`build_epub.sh` 已内置 `chardet` 自动检测编码 + `iconv` 转码。但以下情况仍可能出问题：

1. **`chardet` 没安装** → 脚本会跳过检测，直接喂给 pandoc → 乱码。务必确保 `pip3 install chardet`。
2. **文件扩展名不是 .txt 或 .md** → 脚本跳过编码检测 → 乱码。
3. **生成后用 pandoc 验证内容**：

```bash
# 验证 EPUB 文本是否可读（如果输出含 � 或乱码字符，说明编码有问题）
pandoc output.epub -t plain 2>/dev/null | head -20
```

肉眼确认前几行中文显示正常，再上传。如果发现乱码：

- 用 `file --mime-encoding input.txt` 查看原文件编码
- 手动转码：`iconv -f GBK -t UTF-8 input.txt > input_utf8.txt`
- 再用转码后的文件跑 `build_epub.sh`

如果生成失败：
- 尝试中间格式：`pandoc input.md -o temp.html && pandoc temp.html -o output.epub`
- 检查源文件编码（特别是 PDF 和 DOCX）

### 文件命名规范

`[标题]-YYYYMMDD.epub`

- 标题超 30 字则截断
- 特殊字符替换为 `-`

## 上传到微信读书

```bash
# 检查登录状态
python3 scripts/upload_weread.py --check

# 上传 EPUB
python3 scripts/upload_weread.py output.epub
```

上传使用 Playwright 浏览器自动化，模拟真实用户在 `https://weread.qq.com/web/upload` 页面选择文件，浏览器自动完成腾讯云 COS 分片上传。

**首次使用前需手动获取一次 Cookie**：F12 → Application → Cookies → 保存 `wr_vid`、`wr_skey`、`wr_rt` 到 `~/.web2epub/weread_cookies.json`。

Cookie 会过期（数天到数周），过期后 `--check` 会提示，重新获取即可。

## 错误处理

| 问题 | 处理方式 |
|------|---------|
| URL 无法访问 | 告知用户，建议检查链接是否有效 |
| 内容提取为空 | 用 `favor_recall=True` 重试，或让用户直接提供文字内容 |
| pandoc 转换失败 | 检查文件编码，尝试 HTML 中间格式 |
| 微信读书上传失败 | 检查 cookies（`--check`），确认 Playwright 已安装 |
| 翻译 API key 未配置 | 提示设置 `OPENAI_API_KEY` |

## 微信读书限制

- 非付费会员：每月约 3 本导入额度（2024年起）
- 付费会员：无限制或更高额度
- 单文件最大 50MB
- 上传的书籍笔记默认为私密
