#!/usr/bin/env python3
"""WeRead login helper - opens browser, captures cookies after QR login.

Usage:
  # Launch login flow (opens browser, waits for QR scan)
  python3 weread_login.py

  # After login, cookies are auto-saved to ~/.web2epub/weread_cookies.json
"""

import json
import os
import sys
import time
import webbrowser
from pathlib import Path

CONFIG_DIR = Path.home() / ".web2epub"

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def find_qr_element(page):
    """Try to find QR code image on the page."""
    selectors = [
        "img[src*='qrcode']",
        "img[src*='qr']",
        ".qr-code img",
        "#qr-code img",
        ".qrcode img",
        "canvas",
        ".login-qrcode img",
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                return el
        except Exception:
            continue
    return None


def login_with_playwright():
    """Headless WeRead login: show QR code path, poll for login, save cookies."""
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            context = browser.new_context(
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            print("=== 微信读书登录 ===")
            print("正在获取二维码...")
            page.goto("https://weread.qq.com/", wait_until="domcontentloaded", timeout=30000)

            time.sleep(3)

            qr_file = None
            qr_el = find_qr_element(page)
            if qr_el:
                try:
                    qr_file = str(CONFIG_DIR / "weread_qr.png")
                    qr_el.screenshot(path=qr_file)
                    print(f"✓ 二维码已保存至: {qr_file}")
                except Exception:
                    pass

            if qr_file:
                print("请用微信扫描上方二维码登录（或用手机打开微信读书扫码）")
            else:
                page.screenshot(path=str(CONFIG_DIR / "weread_page.png"))
                print(f"⚠ 未找到二维码元素，页面截图已保存至: {CONFIG_DIR / 'weread_page.png'}")
                print("请手动打开 https://weread.qq.com 扫码登录")

            print("等待登录中（最长5分钟）...")

            weread_cookies = {}
            for attempt in range(150):
                time.sleep(2)
                cookies = context.cookies()
                current = {c["name"]: c["value"] for c in cookies if c["name"].startswith("wr_")}
                if current.get("wr_skey") and current.get("wr_vid"):
                    weread_cookies = current
                    print(f"✓ 检测到登录成功!")
                    break
                if attempt % 15 == 0:
                    print(f"  等待扫码... ({attempt * 2}秒)")

            if not weread_cookies:
                print("⚠ 登录超时")
                return False

            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            cookie_file = CONFIG_DIR / "weread_cookies.json"
            cookie_file.write_text(
                json.dumps(weread_cookies, indent=2, ensure_ascii=False)
            )
            print(f"✓ Cookies 已保存至 {cookie_file}")
            print(f"  共获取 {len(weread_cookies)} 个 cookie")

            context.close()
            browser.close()
            return True

    except Exception as e:
        print(f"✗ 登录失败: {e}")
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        return False


def login_manual():
    """Fallback: guide user to manually copy cookies."""
    print("=== 微信读书 Cookie 配置 ===")
    print("\n请手动操作：")
    print("1. 用 Chrome 打开 https://weread.qq.com")
    print("2. 用微信扫码登录")
    print("3. 按 F12 → Application → Cookies → 选择 weread.qq.com")
    print("4. 运行以下命令粘贴 Cookie JSON：")
    print()
    print("   python3 -c \"")
    print("     import json, pathlib")
    print("     cookie_str = input('Paste cookies JSON: ')")
    print("     pathlib.Path.home().joinpath('.web2epub/weread_cookies.json').write_text(cookie_str)")
    print("     print('Saved!')")
    print("   \"")
    print()

    webbrowser.open("https://weread.qq.com/")
    return False


if __name__ == "__main__":
    if not HAS_PLAYWRIGHT:
        print("⚠ Playwright 未安装，使用手动模式")
        print("  安装: pip3 install --break-system-packages playwright")
        login_manual()
    else:
        if not login_with_playwright():
            print("\n自动登录失败，切换手动模式...")
            login_manual()
