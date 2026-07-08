# 微信读书 WeRead 配置指南

## 方式一：API Key（推荐，用于数据查询）

微信读书现在提供官方 API Key，可用于搜索、书架、笔记等数据查询能力。

### 获取 API Key

1. 打开 https://weread.qq.com/r/weread-skills
2. 用微信扫码登录
3. 在页面中获取 API Key（格式 `wrk-xxxxxxxx...`）

### 配置

```bash
# 方法1：使用 weread-cli
npm install -g weread-agent-cli
weread config set-key "wrk-xxxxxxxx..."

# 方法2：使用环境变量
export WEREAD_API_KEY="wrk-xxxxxxxx..."
```

### 安装 weread-cli

```bash
npm install -g weread-agent-cli
weread doctor  # 验证配置
```

### 验证

```bash
weread search "三体" --scope book --count 3
```

## 方式二：Cookies + Playwright（上传本地书籍到书架）

微信读书网页版的上传功能使用**腾讯云 COS 分片上传**，需要通过 Playwright 浏览器自动化完成。Cookie 用于保持登录状态。

### 安装 Playwright

```bash
pip3 install playwright
playwright install chromium
```

### 获取 Cookies

1. 用 Chrome 打开 https://weread.qq.com
2. 用微信手机 App 扫码登录
3. 按 F12 打开开发者工具 → Application → Cookies
4. 找到 `https://weread.qq.com` 的 Cookies
5. 复制关键 Cookie 值：`wr_vid`、`wr_skey`、`wr_rt`、`wr_localvid`
6. 保存到 `~/.web2epub/weread_cookies.json`

### 验证 Cookies

```bash
python scripts/upload_weread.py --check
```

## 上传文件

```bash
python scripts/upload_weread.py /path/to/book.epub
```

上传流程：
1. Playwright 打开 `https://weread.qq.com/web/upload`
2. 自动点击文件选择面板
3. 模拟选取本地文件
4. 浏览器自动执行：获取 COS 凭证 → 分片上传到腾讯云 → 通知服务器
5. 文件出现在微信读书书架中

### 注意事项

- Cookie 会过期（通常几天到几周），过期后需要重新获取
- 非付费会员每月导入有数量限制（通常 3 本/月，2024年起）
- 最大文件大小 50MB
- 支持格式：EPUB、PDF、TXT、DOC、DOCX、MOBI、AZW3 等
- 上传的书籍笔记默认为私密
