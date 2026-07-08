#!/usr/bin/env python3
"""Upload EPUB/PDF/TXT to WeRead (微信读书) bookshelf.

Usage:
  # Upload a file:
  python upload_weread.py path/to/book.epub

  # Check auth status:
  python upload_weread.py --check

Requires:
  - playwright (`pip install playwright && playwright install chromium`)
  - Cookies saved at ~/.web2epub/weread_cookies.json
"""

import sys
import json
import time
import webbrowser
from pathlib import Path

CONFIG_DIR = Path.home() / ".web2epub"
COOKIE_FILE = CONFIG_DIR / "weread_cookies.json"
WEREAD_UPLOAD_URL = "https://weread.qq.com/web/upload"


def _load_cookies() -> dict:
    if COOKIE_FILE.exists():
        return json.loads(COOKIE_FILE.read_text())
    return {}


def _save_cookies(cookies: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    COOKIE_FILE.write_text(json.dumps(cookies, indent=2, ensure_ascii=False))
    print(f"Cookies saved to {COOKIE_FILE}")


def check_auth() -> bool:
    cookies = _load_cookies()
    if not cookies:
        print("未找到已保存的 cookies，确保已配置或使用 --save-cookies")
        return False

    try:
        import requests
    except ImportError:
        print("需要安装 requests: pip install requests")
        return False

    try:
        resp = requests.get(
            "https://weread.qq.com/web/shelf/sync",
            cookies={k: v for k, v in cookies.items() if k.startswith("wr_")},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if "books" in data or "synckey" in data:
                print("✓ WeRead 认证有效")
                return True
        print(f"✗ 认证失败 (HTTP {resp.status_code})")
        return False
    except Exception as e:
        print(f"✗ 认证检查失败: {e}")
        return False


def upload(filepath: str) -> bool:
    path = Path(filepath)
    if not path.exists():
        print(f"✗ 文件不存在: {filepath}")
        return False

    ext = path.suffix.lower()
    if ext not in (".epub", ".pdf", ".txt", ".doc", ".docx", ".mobi", ".azw3", ".fb2", ".rtf", ".lit", ".cbr", ".cbz"):
        print(f"✗ 不支持的文件格式: {ext}")
        return False

    cookies = _load_cookies()
    if not cookies:
        print("✗ 未配置 cookies")
        return False

    file_size_mb = path.stat().st_size / (1024 * 1024)
    print(f"上传中: {path.name} ({file_size_mb:.1f} MB)")
    print(f"目标: WeRead 书架")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("✗ 请先安装 playwright: pip install playwright && playwright install chromium")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        context.add_cookies([
            {"name": k, "value": v, "domain": ".weread.qq.com", "path": "/"}
            for k, v in cookies.items()
        ])

        page = context.new_page()
        page.goto(WEREAD_UPLOAD_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        with page.expect_file_chooser() as fc_info:
            page.click(".bookUpload_fileSelectPanel", timeout=5000)

        file_chooser = fc_info.value
        file_chooser.set_files(str(path.absolute()))
        print("  文件已选择，正在上传...")

        max_wait = max(120, int(file_size_mb * 10))
        page.wait_for_timeout(max_wait * 1000)

        result_elem = page.query_selector(".bookUpload_result")
        if result_elem:
            text = result_elem.text_content()
            print(f"  上传结果: {text}")
            browser.close()
            return "成功" in text or "完成" in text or "已导入" in text

        browser.close()
        print("✓ 上传完成（请到书架确认）")
        return True


def open_weread_upload():
    webbrowser.open(WEREAD_UPLOAD_URL)
    print("已打开微信读书上传页面，登录后可拖拽文件上传")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "--check":
        check_auth()
    elif cmd == "--open":
        open_weread_upload()
    elif cmd.startswith("--"):
        print(f"Unknown: {cmd}")
        sys.exit(1)
    else:
        upload(cmd)
